import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import differential_evolution
from scipy.optimize import minimize
from scipy.sparse.linalg import spsolve
from scipy.sparse import coo_matrix
from .mcmc import mcmc

import itertools
import time
import torch
from functools import partial
from hgdl.hgdl import HGDL



class gpHGDL():
    """
    gpHGDL class: Provides all tool for a single-task GP tuned for HGDL optimization.

    symbols:
        N: Number of points in the data set
        n: number of return values
        dim1: number of dimension of the input space

    Attributes:
        input_space_dim (int):         dim1
        points (N x dim1 numpy array): 2d numpy array of points
        values (N dim numpy array):    2d numpy array of values
        init_hyperparameters:          1d numpy array (>0)

    Optional Attributes:
        variances (N dim numpy array):                  variances of the values, default = array of shape of points
                                                        with 1 % of the values
        compute_device:                                 cpu/gpu, default = cpu
        gp_kernel_function(callable):                   None/function defining the 
                                                        kernel def name(x1,x2,hyperparameters,self), 
                                                        make sure to return a 2d numpy array, default = None uses default kernel
        gp_mean_function(callable):                     None/function def name(gp_obj, x, hyperparameters), 
                                                        make sure to return a 1d numpy array, default = None
        sparse (bool):                                  default = False
        normalize_y:                                    default = False, normalizes the values \in [0,1]

    Example:
        obj = fvGP(3,np.array([[1,2,3],[4,5,6]]),
                         np.array([2,4]),
                         np.array([2,3,4,5]),
                         variances = np.array([0.01,0.02]),
                         gp_kernel_function = kernel_function,
                         gp_mean_function = some_mean_function
        )
    """

    def __init__(
        self,
        input_space_dim,
        points,
        values,
        init_hyperparameters,
        variances = None,
        compute_device = "cpu",
        gp_kernel_function = None,
        gp_kernel_function_grad = None,
        gp_mean_function = None,
        gp_mean_function_grad = None,
        sparse = False,
        normalize_y = False,
        use_inv = False,
        ram_economy = True,
        ):
        """
        The constructor for the gp class.
        type help(GP) for more information about attributes, methods and their parameters
        """
        if input_space_dim != len(points[0]):
            raise ValueError("input space dimensions are not in agreement with the point positions given")
        if np.ndim(values) == 2: values = values[:,0]

        self.normalize_y = normalize_y
        self.input_dim = input_space_dim
        self.x_data = torch.tensor(points, dtype = float)#, requires_grad = True)
        self.point_number = len(self.x_data)
        self.y_data = torch.tensor(values, dtype = float)#, requires_grad = True)
        self.compute_device = compute_device
        self.ram_economy = ram_economy
        #self.gp_kernel_function_grad = gp_kernel_function_grad
        #self.gp_mean_function_grad = gp_mean_function_grad

        self.sparse = sparse
        self.use_inv = use_inv
        self.K_inv = None
        if self.normalize_y is True: self._normalize_y_data()
        ##########################################
        #######prepare variances##################
        ##########################################
        if variances is None:
            #, requires_grad = True) *
            self.variances = torch.ones((self.y_data.shape), dtype = float) * \
                    abs(self.y_data / 100.0)
            print("CAUTION: you have not provided data variances in fvGP,")
            print("they will be set to 1 percent of the data values!")
        elif variances.dim() == 2:
            self.variances = variances[:,0]
        elif variances.dim() == 1:
            self.variances = torch.tensor(variances, dtype = float)#, requires_grad = True)
        else:
            raise Exception("Variances are not given in an allowed format. Give variances as 1d numpy array")
        if len(self.variances[self.variances < 0]) > 0: raise Exception("Negative measurement variances communicated to fvgp.")
        ##########################################
        #######define kernel and mean function####
        ##########################################
        if callable(gp_kernel_function): self.kernel = gp_kernel_function
        else: self.kernel = self.default_kernel
        self.d_kernel_dx = self.d_gp_kernel_dx

        self.gp_mean_function = gp_mean_function
        if  callable(gp_mean_function): self.mean_function = gp_mean_function
        else: self.mean_function = self.default_mean_function

        if callable(gp_kernel_function_grad): self.dk_dh = gp_kernel_function_grad
        else:
            if self.ram_economy is True: self.dk_dh = self.gp_kernel_derivative
            else: self.dk_dh = self.gp_kernel_gradient

        if callable(gp_mean_function_grad): self.dm_dh = gp_mean_function_grad
        ##########################################
        #######prepare hyper parameters###########
        ##########################################
        #print(self.x_data)
        #print(self.y_data)
        #print(self.variances)
        self.hyperparameters = torch.tensor(init_hyperparameters, dtype = float) #,requires_grad = True)
        #print(self.hyperparameters)
        #print("====================================")
        ##########################################
        #compute the prior########################
        ##########################################
        self.compute_prior_fvGP_pdf()
        print("fvGP successfully initiated")

    def update_gp_data(
        self,
        points,
        values,
        variances = None,
        ):

        """
        This function updates the data in the gp_class.
        The data will NOT be appended but overwritten!
        Please provide the full updated data set

        Attributes:
            points (N x dim1 numpy array): A 2d  array of points.
            values (N)                   : A 1d  array of values.

        Optional Attributes:
            variances (N)                : variances for the values
        """
        if self.input_dim != len(points[0]):
            raise ValueError("input space dimensions are not in agreement with the point positions given")
        if np.ndim(values) == 2: values = values[:,0]

        self.x_data = torch.tensor(points, dtype = float) #, requires_grad = True)
        self.point_number = len(self.x_data)
        self.y_data = torch.tensor(values, dtype = float) #, requires_grad = True)

        if self.normalize_y is True: self._normalize_y_data()
        ##########################################
        #######prepare variances##################
        ##########################################
        if variances is None:
            #, requires_grad = True
            self.variances = torch.ones((self.y_data.shape), dtype = float) * abs(self.y_data / 100.0)
            print("CAUTION: you have not provided data variances in fvGP,")
            print("they will be set to 1 percent of the data values!")
        elif variances.dim() == 2:
            self.variances = variances[:,0]
        elif variances.dim() == 1:
            self.variances = torch.tensor(variances, dtype = float) #, requires_grad = True)
        else:
            raise Exception("Variances are not given in an allowed format. Give variances as 1d numpy array")

        if len(self.variances[self.variances < 0]) > 0: raise Exception("Negative measurement variances communicated to fvgp.")
        ######################################
        #####transform to index set###########
        ######################################
        self.compute_prior_fvGP_pdf()
        print("fvGP data updated")
    ###################################################################################
    ###################################################################################
    ###################################################################################
    #################TRAINING##########################################################
    ###################################################################################
    def stop_training(self,opt_obj):
        print("fvGP is cancelling the asynchronous training...")
        try: opt_obj.cancel_tasks(); print("fvGP successfully cancelled the current training.")
        except: print("No asynchronous training to be cancelled in fvGP, no training is running.")
    ###################################################################################
    def kill_training(self,opt_obj):
        print("fvGP is killing asynchronous training....")
        try: opt_obj.kill_client(); print("fvGP successfully killed the training.")
        except: print("No asynchronous training to be killed, no training is running.")
    ###################################################################################
    ##################################################################################
    def train_async(self,
        hyperparameter_bounds,
        init_hyperparameters = None,
        max_iter = 10000,
        local_optimizer = "L-BFGS-B",
        global_optimizer = "genetic",
        deflation_radius = None,
        dask_client = None):
        """
        This function finds the maximum of the log_likelihood and therefore trains the 
        GP (aynchronously) using 'hgdl'.
        This can be done on a remote cluster/computer by providing the right dask client

        inputs:
            hyperparameter_bounds (2d list)
        optional inputs:
            init_hyperparameters (list):  default = None
            max_iter: default = 120,
            local_optimizer = "L-BFGS-B"
            global_optimizer = "genetic"
            deflation_radius = None
            dask_client: True/False/dask client, default = None (will use a local client)

        output:
            returns an optimization object that can later be queried for solutions
            stopped and killed.
        """
        ############################################
        if dask_client is None: dask_client = distributed.Client()
        if init_hyperparameters is None:
            init_hyperparameters = self.hyperparameters.detach().numpy()
        print("Async fvGP training started with ",len(self.x_data)," data points")
        ######################
        #####TRAINING#########
        ######################
        opt_obj = self.optimize_log_likelihood_async(
            init_hyperparameters,
            hyperparameter_bounds,
            max_iter,
            local_optimizer,
            global_optimizer,
            deflation_radius,
            dask_client
            )
        return opt_obj
        ######################
        ######################
        ######################
    ##################################################################################
    def update_hyperparameters(self, opt_obj):
        print("Updating the hyperparameters in fvGP...")
        try:
            res = opt_obj.get_latest(1)["x"][0]
            l_n = self.log_likelihood(res)
            l_o = self.log_likelihood_torch(self.hyperparameters).detach().numpy()
            print("see this")
            if l_n - l_o < 0.000001:
                self.hyperparameters = torch.tensor(res, dtype = float)
                self.compute_prior_fvGP_pdf()
                print("    fvGP async hyperparameter update successful")
                print("    Latest hyperparameters: ", self.hyperparameters)
            else:
                print("    The update was attempted but the new hyperparameters led to a lower likelihood, so I kept the old ones")
                print("Old likelihood: ", -l_o, " at ", self.hyperparameters)
                print("New likelihood: ", -l_n, " at ", res)
        except Exception as e:
            print("    Async Hyper-parameter update not successful in fvGP. I am keeping the old ones.")
            print("    That probably means you are not optimizing them asynchronously")
            print("    Here is the actual reason: ", str(e))
            print("    hyperparameters: ", self.hyperparameters)
        return self.hyperparameters
    ##################################################################################
    def optimize_log_likelihood_async(self,
        starting_hps,
        hp_bounds,
        max_iter,
        local_optimizer,
        global_optimizer,
        deflation_radius,
        dask_client):
        print("fvGP submitted HGDL optimization for asynchronous training")
        print("bounds:",hp_bounds)
        print("deflation radius: ",deflation_radius)
        print("local optimizer: ",local_optimizer)
        print("global optimizer: ",global_optimizer)
        print("starting x: ",starting_hps )
        opt_obj = HGDL(self.log_likelihood,
                    self.log_likelihood_gradient,
                    hp_bounds,
                    hess = self.log_likelihood_hessian,
                    local_optimizer = local_optimizer,
                    global_optimizer = global_optimizer,
                    radius = deflation_radius,
                    num_epochs = max_iter)
        opt_obj.optimize(dask_client = dask_client, x0 = starting_hps)
        return opt_obj
    ##################################################################################
    def log_likelihood(self,hyperparameters):
        res = self.log_likelihood_torch(torch.tensor(hyperparameters, dtype = float))
        return res.detach().numpy()

    def log_likelihood_torch(self,hyperparameters):
        """
        computes the marginal log-likelihood
        input:
            hyper parameters
        output:
            negative marginal log-likelihood (scalar)
        """
        mean = self.mean_function(self,self.x_data,hyperparameters)
        if mean.ndim > 1: raise Exception("Your mean function did not return a 1d numpy array!")
        x,K = self._compute_covariance_value_product(hyperparameters,self.y_data, self.variances, mean)
        y = self.y_data - mean
        sign, logdet = self.slogdet(K)
        n = len(y)
        if sign == 0.0: return (0.5 * (y.T @ x)) + (0.5 * n * np.log(2.0*np.pi))
        return (0.5 * (y.T @ x)) + (0.5 * sign * logdet) + (0.5 * n * np.log(2.0*np.pi))
    ##################################################################################
    def log_likelihood_gradient(self, hyperparameters):
        res = self.log_likelihood_gradient_torch(torch.tensor(hyperparameters, dtype = float))
        return res.detach().numpy()

    def log_likelihood_gradient_torch(self, hyperparameters, autograd = True):
        """
        computes the gradient of the negative marginal log-likelihood
        input:
            hyper parameters
        output:
            gradient of the negative marginal log-likelihood (vector)
        """
        return torch.autograd.functional.jacobian(self.log_likelihood_torch,hyperparameters)



    def log_likelihood_gradient_torch_analytical(self, hyperparameters, K_inv = None):
        """
        computes the gradient of the negative marginal log-likelihood
        input:
            hyper parameters
        output:
            gradient of the negative marginal log-likelihood (vector)
        """
        mean = self.mean_function(self,self.x_data,hyperparameters)
        b,K = self._compute_covariance_value_product(hyperparameters,self.y_data, self.variances, mean)
        y = self.y_data - mean
        bbT = torch.outer(b , b.T)
        dL_dH = torch.zeros((len(hyperparameters)))
        dL_dHm = torch.zeros((len(hyperparameters)))
        dm_dh = self.dm_dh(hyperparameters)

        for i in range(len(hyperparameters)):
            dL_dHm[i] = -dm_dh[i].T @ b
            dK_dH = self.dk_dh(self.x_data,self.x_data, i,hyperparameters)
            matr = self.solve(K,dK_dH)
            if dL_dHm[i] == 0.0:
                mtrace = torch.einsum('ij,ji->', bbT, dK_dH)
                dL_dH[i] = - 0.5 * (mtrace - torch.trace(matr))
            else:
                dL_dH[i] = 0.0
        return dL_dH + dL_dHm

    def log_likelihood_gradient_torch_hybrid(self, hyperparameters, K_inv = None):
        """
        computes the gradient of the negative marginal log-likelihood
        input:
            hyper parameters
        output:
            gradient of the negative marginal log-likelihood (vector)
        """
        mean = self.mean_function(self,self.x_data,hyperparameters)
        y = self.y_data - mean
        if K_inv is None: 
            b,K = self._compute_covariance_value_product(hyperparameters,self.y_data, self.variances, mean)
            bbT = torch.outer(b , b.T)
        else:
            bbt.torch.outer(K_inv @ y, K_inv @ y)

        dL_dH = torch.zeros((len(hyperparameters)))
        dL_dHm = torch.zeros((len(hyperparameters)))
        dm_dh = self.mean_function_grad(hyperparameters).t()
        
        for i in range(len(hyperparameters)):
            dL_dHm[i] = -dm_dh[i].T @ b
            dK_dH = self.gp_kernel_gradient_auto(i,hyperparameters)
            print(i, dK_dH)
            matr = self.solve(K,dK_dH)
            if dL_dHm[i] == 0.0:
                mtrace = torch.einsum('ij,ji->', bbT, dK_dH)
                dL_dH[i] = - 0.5 * (mtrace - torch.trace(matr))
            else:
                dL_dH[i] = 0.0
        return dL_dH + dL_dHm


    ##################################################################################
    def log_likelihood_hessian(self, hyperparameters):
        res = self.log_likelihood_hessian_torch(torch.tensor(hyperparameters, dtype = float))
        result = (res.detach().numpy() + res.detach().numpy().T)/2.0
        return result

    def log_likelihood_hessian_torch(self, hyperparameters, autograd = True):
        """
        computes the hessian of the negative  marginal  log-likelihood
        input:
            hyper parameters
        output:
            hessian of the negative marginal log-likelihood (matrix)
        """
        return torch.autograd.functional.hessian(self.log_likelihood_torch,hyperparameters)
    ##################################################################################
    ##################################################################################
    ##################################################################################
    ##################################################################################
    ######################Compute#Covariance#Matrix###################################
    ##################################################################################
    ##################################################################################
    def compute_prior_fvGP_pdf(self):
        """
        This function computes the important entities, namely the prior covariance and
        its product with the (values - prior_mean) and returns them and the prior mean
        input:
            none
        return:
            prior mean
            prior covariance
            covariance value product
        """
        self.prior_mean_vec = self.mean_function(self,self.x_data,self.hyperparameters)
        cov_y,K = self._compute_covariance_value_product(
                self.hyperparameters,
                self.y_data,
                self.variances,
                self.prior_mean_vec)
        self.prior_covariance = K
        if self.use_inv is True: self.K_inv = self.inv(K)
        self.covariance_value_prod = cov_y
    ##################################################################################
    def _compute_covariance_value_product(self, hyperparameters,values, variances, mean):
        K = self.compute_covariance(hyperparameters, variances)
        y = values - mean
        x = self.solve(K, y)
        #if self.use_inv is True: x = self.K_inv @ y
        #else: x = self.solve(K, y)
        if x.ndim == 2: x = x[:,0]
        return x,K
    ##################################################################################
    def compute_covariance(self, hyperparameters, variances):
        """computes the covariance matrix from the kernel"""
        CoVariance = self.kernel(
            self.x_data, self.x_data, hyperparameters, self)
        self.add_to_diag(CoVariance, variances)
        return CoVariance

    def slogdet(self, A):
        """
        fvGPs slogdet method based on torch
        """
        #s,l = np.linalg.slogdet(A)
        #return s,l
        if self.compute_device == "cpu":
            sign, logdet = torch.slogdet(A)
            logdet = torch.nan_to_num(logdet)
            return sign, logdet
        elif self.compute_device == "gpu" or self.compute_device == "multi-gpu":
            sign, logdet = torch.slogdet(A)
            sign = sign.cpu()
            logdet = logdet.cpu()
            logdet = torch.nan_to_num(logdet)
            return sign, logdet

    def inv(self, A):
            B = torch.inverse(A)
            return B

    def solve(self, A, b):
        """
        fvGPs slogdet method based on torch
        """
        #x = np.linalg.solve(A,b)
        #return x
        #if b.dim() == 1: b = np.expand_dims(b,axis = 1)
        if self.compute_device == "cpu":
        #    #####for sparsity:
        #    if self.sparse == True:
        #        zero_indices = np.where(A < 1e-16)
        #        A[zero_indices] = 0.0
        #        if self.is_sparse(A):
        #            try:
        #                A = scipy.sparse.csr_matrix(A)
        #                x = scipy.sparse.spsolve(A,b)
        #                return x
        #            except Exceprion as e:
        #                print("fvGP: Sparse solve did not work out.")
        #                print("reason: ", str(e))
            ##################
            try:
                x = torch.linalg.solve(A,b)
                return x
            except Exception as e:
                try:
                    print("fvGP: except statement invoked: torch.solve() on cpu did not work")
                    print("reason: ", str(e))
                    #x, qr = torch.lstsq(b,A)
                    x, qr = torch.linalg.lstsq(A,b)
                except Exception as e:
                    print("fvGP: except statement 2 invoked: torch.solve() and torch.lstsq() on cpu did not work")
                    print("falling back to numpy.lstsq()")
                    print("reason: ", str(e))
                    x,res,rank,s = torch.linalg.lstsq(A,b)
                    return x
            return x
        elif self.compute_device == "gpu" or A.ndim < 3:
            A = A.to(device = "cuda")
            b = b.to(device = "cuda")
            try:
                x = torch.linalg.solve(A, b)
            except Exception as e:
                print("fvGP: except statement invoked: torch.solve() on gpu did not work")
                print("reason: ", str(e))
                x,res,rank,s = torch.linalg.lstsq(A,b)
            return x.cpu()
        #elif self.compute_device == "multi-gpu":
        #    n = min(len(A), torch.cuda.device_count())
        #    split_A = torch.tensor_split(A,n)
        #    split_b = torch.tensor_split(b,n)
        #    results = []
        #    for i, (tmp_A,tmp_b) in enumerate(zip(split_A,split_b)):
        #        cur_device = torch.device("cuda:"+str(i))
        #        tmp_A = tmp_A.to(device = cur_device)
        #        tmp_b = tmp_b.to(device = cur_device)
        #        results.append(torch.linalg.solve(tmp_A,tmp_b)[0])
        #    total = results[0].cpu()
        #    for i in range(1,len(results)):
        #        total = np.append(total, results[i].cpu().numpy(), 0)
        #    return total
    ##################################################################################
    def add_to_diag(self,Matrix, Vector):
        d = torch.einsum("ii->i", Matrix)
        d += Vector
        return Matrix
    #def is_sparse(self,A):
    #    if float(np.count_nonzero(A))/float(len(A)**2) < 0.01: return True
    #    else: return False
    #def how_sparse_is(self,A):
    #    return float(np.count_nonzero(A))/float(len(A)**2)
    def default_mean_function(self,gp_obj,x,hyperparameters):
        """evaluates the gp mean function at the data points """
        #, requires_grad = True
        mean = torch.ones((len(x)), dtype = float) + torch.mean(self.y_data, dtype = float)
        return mean

    def mean_function_grad(self,hyperparameters):
        """evaluates the gp mean function at the data points """
        m = partial(self.mean_function, self, self.x_data)
        grad = torch.autograd.functional.jacobian(m,hyperparameters)
        return grad

    ###########################################################################
    ###########################################################################
    ###########################################################################
    ###############################gp prediction###############################
    ###########################################################################
    ###########################################################################
    def posterior_mean(self, x_iset):
        """
        function to compute the posterior mean
        input:
        ------
            x_iset: 2d numpy array of points, note, these are elements of the 
            index set which results from a cartesian product of input and output space
        output:
        -------
            {"x":    the input points,
             "f(x)": the posterior mean vector (1d numpy array)}
        """
        p = torch.tensor(x_iset, dtype = float)
        if p.dim() == 1: p = p[None, :]
        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        A = k.T @ self.covariance_value_prod
        posterior_mean = self.mean_function(self,p,self.hyperparameters) + A
        return {"x": p,
                "f(x)": posterior_mean}

    def posterior_mean_grad(self, x_iset, direction):
        """
        function to compute the gradient of the posterior mean in
        a specified direction
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the
                    index set which results from a cartesian product of input and output space
            direction: direction in which to compute the gradient
        output:
        -------
            {"x":    the input points,
             "direction": the direction
             "df/dx": the gradient of the posterior mean vector (1d numpy array)}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        x1 = np.array(p)
        x2 = np.array(p)
        eps = 1e-6
        x1[:,direction] = x1[:,direction] + eps
        x2[:,direction] = x2[:,direction] - eps
        mean_der = (self.mean_function(self,x1,self.hyperparameters) - self.mean_function(self,x2,self.hyperparameters))/(2.0*eps)
        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        k_g = self.d_kernel_dx(p,self.x_data, direction,self.hyperparameters)
        posterior_mean_grad = mean_der + (k_g @ self.covariance_value_prod)
        return {"x": p,
                "direction":direction,
                "df/dx": posterior_mean_grad}

    ###########################################################################
    def posterior_covariance(self, x_iset, variance_only = False):
        """
        function to compute the posterior covariance
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
            index set which results from a cartesian product of input and output space
        output:
        -------
            {"x":    the index set points,
             "v(x)": the posterior variances (1d numpy array) for each input point,
             "S":    covariance matrix, v(x) = diag(S)}
        """
        p = torch.tensor(x_iset, dtype = float)
        if p.dim() == 1: p = p[None, :]

        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        kk = self.kernel(p, p,self.hyperparameters,self)
        if self.use_inv is True:
            if variance_only is True: v = np.diag(kk) - np.einsum('ij,jk,ki->i', k.T, self.K_inv, k); S = False
            if variance_only is False:  S = kk - (k.T @ self.K_inv @ k); v = np.diag(S)
        else:
            k_cov_prod = self.solve(self.prior_covariance,k)
            S = kk - (k_cov_prod.T @ k)
            v = torch.diag(S)
        if len(v[ v < -0.001]) > 0:
            print("In fvGP: CAUTION, negative variances encountered. That normally means that the model is unstable.")
            print("Rethink the kernel definitions, add more noise to the data,")
            print("or double check the hyperparameter optimization bounds. This will not ")
            print("terminate the algorithm, but expect anomalies.")
            print("diagonal of the posterior covariance: ",v)
            raise Exception("EXIT")

        return {"x": p,
                "v(x)": v,
                "S(x)": S}

    def posterior_covariance_grad(self, x_iset,direction):
        """
        function to compute the gradient of the posterior covariance
        in a specified direction
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the
                    index set which results from a cartesian product of input and output space
            direction: direction in which the gradient to compute
        output:
        -------
            {"x":    the index set points,
             "dv/dx": the posterior variances (1d numpy array) for each input point,
             "dS/dx":    covariance matrix, v(x) = diag(S)}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        k_g = self.d_kernel_dx(p,self.x_data, direction,self.hyperparameters).T
        kk =  self.kernel(p, p,self.hyperparameters,self)
        x1 = np.array(p)
        x2 = np.array(p)
        eps = 1e-6
        x1[:,direction] = x1[:,direction] + eps
        x2[:,direction] = x2[:,direction] - eps
        kk_g = (self.kernel(x1, x1,self.hyperparameters,self)-self.kernel(x2, x2,self.hyperparameters,self)) /(2.0*eps)
        k_covariance_prod = self.solve(self.prior_covariance,k)
        k_g_covariance_prod = self.solve(self.prior_covariance,k_g)
        a = kk_g - ((k_covariance_prod.T @ k_g) + (k_g_covariance_prod.T @ k))
        return {"x": p,
                "dv/dx": np.diag(a),
                "dS/dx": a}

    ###########################################################################
    def gp_prior(self, x_iset):
        """
        function to compute the data-informed prior
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
        output:
        -------
            {"x": the index set points,
             "K": covariance matrix between data points
             "k": covariance between data and requested poins,
             "kappa": covariance matrix between requested points,
             "prior mean": the mean of the prior
             "S:": joint prior covariance}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        kk = self.kernel(p, p,self.hyperparameters,self)
        post_mean = self.mean_function(self,p, self.hyperparameters)
        full_gp_prior_mean = np.append(self.prior_mean_vec, post_mean)
        return  {"x": p,
                 "K": self.prior_covariance,
                 "k": k,
                 "kappa": kk,
                 "prior mean": full_gp_prior_mean,
                 "S(x)": np.block([[self.prior_covariance, k],[k.T, kk]])}
    ###########################################################################
    def gp_prior_grad(self, x_iset,direction):
        """
        function to compute the gradient of the data-informed prior
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the
                    index set which results from a cartesian product of input and output space
            direction: direction in which to compute the gradient
        output:
        -------
            {"x": the index set points,
             "K": covariance matrix between data points
             "k": covariance between data and requested poins,
             "kappa": covariance matrix between requested points,
             "prior mean": the mean of the prior
             "dS/dx:": joint prior covariance}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        kk = self.kernel(p, p,self.hyperparameters,self)
        k_g = self.d_kernel_dx(p,self.x_data, direction,self.hyperparameters).T
        x1 = np.array(p)
        x2 = np.array(p)
        eps = 1e-6
        x1[:,direction] = x1[:,direction] + eps
        x2[:,direction] = x2[:,direction] - eps
        kk_g = (self.kernel(x1, x1,self.hyperparameters,self)-self.kernel(x2, x2,self.hyperparameters,self)) /(2.0*eps)
        post_mean = self.mean_function(self,p, self.hyperparameters)
        mean_der = (self.mean_function(self,x1,self.hyperparameters) - self.mean_function(self,x2,self.hyperparameters))/(2.0*eps)
        full_gp_prior_mean_grad = np.append(np.zeros((self.prior_mean_vec.shape)), mean_der)
        prior_cov_grad = np.zeros(self.prior_covariance.shape)
        return  {"x": p,
                 "K": self.prior_covariance,
                 "dk/dx": k_g,
                 "d kappa/dx": kk_g,
                 "d prior mean/x": full_gp_prior_mean_grad,
                 "dS/dx": np.block([[prior_cov_grad, k_g],[k_g.T, kk_g]])}

    ###########################################################################

    def entropy(self, S):
        """
        function comuting the entropy of a normal distribution
        res = entropy(S); S is a 2d numpy array, matrix has to be non-singular
        """
        dim  = len(S[0])
        s, logdet = self.slogdet(S)
        return (float(dim)/2.0) +  ((float(dim)/2.0) * np.log(2.0 * np.pi)) + (0.5 * s * logdet)
    ###########################################################################
    def gp_entropy(self, x_iset):
        """
        function to compute the entropy of the data-informed prior
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the
                    index set which results from a cartesian product of input and output space
        output:
        -------
            scalar: entropy
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        priors = self.gp_prior(p)
        S = priors["S(x)"]
        dim  = len(S[0])
        s, logdet = self.slogdet(S)
        return (float(dim)/2.0) +  ((float(dim)/2.0) * np.log(2.0 * np.pi)) + (0.5 * s * logdet)
    ###########################################################################
    def gp_entropy_grad(self, x_iset,direction):
        """
        function to compute the gradient of the entropy of the data-informed prior
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the
                    index set which results from a cartesian product of input and output space
            direction: direction in which to compute the gradient
        output:
        -------
            scalar: entropy gradient
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        priors1 = self.gp_prior(p)
        priors2 = self.gp_prior_grad(p,direction)
        S1 = priors1["S(x)"]
        S2 = priors2["dS/dx"]
        return 0.5 * np.trace(np.linalg.inv(S1) @ S2)
    ###########################################################################
    def kl_div(self,mu1, mu2, S1, S2):
        """
        function computing the KL divergence between two normal distributions
        a = kl_div(mu1, mu2, S1, S2); S1, S2 are a 2d numpy arrays, matrices has to be non-singular
        mu1, mu2 are mean vectors, given as 2d arrays
        returns a real scalar
        """
        s1, logdet1 = self.slogdet(S1)
        s2, logdet2 = self.slogdet(S2)
        x1 = self.solve(S2,S1)
        mu = np.subtract(mu2,mu1)
        x2 = self.solve(S2,mu)
        dim = len(mu)
        kld = 0.5 * (np.trace(x1) + (x2.T @ mu) - dim + ((s2*logdet2)-(s1*logdet1)))
        if kld < -1e-4: print("fvGP: Negative KL divergence encountered")
        return kld
    ###########################################################################
    def kl_div_grad(self,mu1,dmu1dx, mu2, S1, dS1dx, S2):
        """
        function comuting the gradient of the KL divergence between two normal distributions
        when the gradients of the mean and covariance are given
        a = kl_div(mu1, dmudx,mu2, S1, dS1dx, S2); S1, S2 are a 2d numpy arrays, matrices has to be non-singular
        mu1, mu2 are mean vectors, given as 2d arrays
        """
        s1, logdet1 = self.slogdet(S1)
        s2, logdet2 = self.slogdet(S2)
        x1 = self.solve(S2,dS1dx)
        mu = np.subtract(mu2,mu1)
        x2 = self.solve(S2,mu)
        x3 = self.solve(S2,-dmu1dx)
        dim = len(mu)
        kld = 0.5 * (np.trace(x1) + ((x3.T @ mu) + (x2 @ -dmu1dx)) - np.trace(np.linalg.inv(S1) @ dS1dx))
        if kld < -1e-4: print("In fvGP: Negative KL divergence encountered")
        return kld
    ###########################################################################
    def gp_kl_div(self, x_iset, comp_mean, comp_cov):
        """
        function to compute the kl divergence of a posterior at given points
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
        output:
        -------
            {"x": the index set points,
             "gp posterior mean": ,
             "gp posterior covariance":  ,
             "given mean": the user-provided mean vector,
             "given covariance":  the use_provided covariance,
             "kl-div:": the kl div between gp pdf and given pdf}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        res = self.posterior_mean(p)
        gp_mean = res["f(x)"]
        gp_cov = self.posterior_covariance(x_iset)["S(x)"]

        return {"x": p,
                "gp posterior mean" : gp_mean,
                "gp posterior covariance": gp_cov,
                "given mean": comp_mean,
                "given covariance": comp_cov,
                "kl-div": self.kl_div(gp_mean, comp_mean, gp_cov, comp_cov)}


    ###########################################################################
    def gp_kl_div_grad(self, x_iset, comp_mean, comp_cov, direction):
        """
        function to compute the gradient of the kl divergence of a posterior at given points
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
            direction: direction in which the gradient will be computed
        output:
        -------
            {"x": the index set points,
             "gp posterior mean": ,
             "gp posterior mean grad": ,
             "gp posterior covariance":  ,
             "gp posterior covariance grad":  ,
             "given mean": the user-provided mean vector,
             "given covariance":  the use_provided covariance,
             "kl-div grad": the grad of the kl div between gp pdf and given pdf}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        gp_mean = self.posterior_mean(p)["f(x)"]
        gp_mean_grad = self.posterior_mean_grad(p,direction)["df/dx"]
        gp_cov  = self.posterior_covariance(p)["S(x)"]
        gp_cov_grad  = self.posterior_covariance_grad(p,direction)["dS/dx"]

        return {"x": p,
                "gp posterior mean" : gp_mean,
                "gp posterior mean grad" : gp_mean_grad,
                "gp posterior covariance": gp_cov,
                "gp posterior covariance grad": gp_cov_grad,
                "given mean": comp_mean,
                "given covariance": comp_cov,
                "kl-div grad": self.kl_div_grad(gp_mean, gp_mean_grad,comp_mean, gp_cov, gp_cov_grad, comp_cov)}
    ###########################################################################
    def shannon_information_gain(self, x_iset):
        """
        function to compute the shannon-information gain of data
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
        output:
        -------
            {"x": the index set points,
             "prior entropy": prior entropy
             "posterior entropy": posterior entropy
             "sig:" shannon_information gain}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        k = self.kernel(self.x_data,p,self.hyperparameters,self)
        kk = self.kernel(p, p,self.hyperparameters,self)


        full_gp_covariances = \
                np.asarray(np.block([[self.prior_covariance,k],\
                            [k.T,kk]]))

        e1 = self.entropy(self.prior_covariance)
        e2 = self.entropy(full_gp_covariances)
        sig = (e2 - e1)
        return {"x": p,
                "prior entropy" : e1,
                "posterior entropy": e2,
                "sig":sig}
    ###########################################################################
    def shannon_information_gain_grad(self, x_iset, direction):
        """
        function to compute the gradient if the shannon-information gain of data
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
            direction: direction in which to compute the gradient
        output:
        -------
            {"x": the index set points,
             "sig_grad:" shannon_information gain gradient}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        e2 = self.gp_entropy_grad(p,direction)
        sig = e2
        return {"x": p,
                "sig grad":sig}
    ###########################################################################
    def posterior_probability(self, x_iset, comp_mean, comp_cov):
        """
        function to compute the probability of an uncertain feature given the gp posterior
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
            comp_mean: a vector of mean values, same length as x_iset
            comp_cov: covarianve matrix, \in R^{len(x_iset)xlen(x_iset)}

        output:
        -------
            {"mu":,
             "covariance": ,
             "probability":  ,
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        res = self.posterior_mean(p)
        gp_mean = res["f(x)"]
        gp_cov = self.posterior_covariance(p)["S(x)"]
        gp_cov_inv = np.linalg.inv(gp_cov)
        comp_cov_inv = np.linalg.inv(comp_cov)
        cov = np.linalg.inv(gp_cov_inv + comp_cov_inv)
        mu =  cov @ gp_cov_inv @ gp_mean + cov @ comp_cov_inv @ comp_mean
        s1, logdet1 = self.slogdet(cov)
        s2, logdet2 = self.slogdet(gp_cov)
        s3, logdet3 = self.slogdet(comp_cov)
        dim  = len(mu)
        C = 0.5*(((gp_mean.T @ gp_cov_inv + comp_mean.T @ comp_cov_inv).T \
               @ cov @ (gp_cov_inv @ gp_mean + comp_cov_inv @ comp_mean))\
               -(gp_mean.T @ gp_cov_inv @ gp_mean + comp_mean.T @ comp_cov_inv @ comp_mean)).squeeze()
        ln_p = (C + 0.5 * logdet1) - (np.log((2.0*np.pi)**(dim/2.0)) + (0.5*(logdet2 + logdet3)))
        return {"mu": mu,
                "covariance": cov,
                "probability": 
                np.exp(ln_p)
                }
    def posterior_probability_grad(self, x_iset, comp_mean, comp_cov, direction):
        """
        function to compute the gradient of the probability of an uncertain feature given the gp posterior
        input:
        ------
            x_iset: 1d or 2d numpy array of points, note, these are elements of the 
                    index set which results from a cartesian product of input and output space
            comp_mean: a vector of mean values, same length as x_iset
            comp_cov: covarianve matrix, \in R^{len(x_iset)xlen(x_iset)}
            direction: direction in which to compute the gradient

        output:
        -------
            {"probability grad":  ,}
        """
        p = np.array(x_iset)
        if p.ndim == 1: p = np.array([p])
        if len(p[0]) != len(self.x_data[0]): p = np.column_stack([p,np.zeros((len(p)))])

        x1 = np.array(p)
        x2 = np.array(p)
        x1[:,direction] = x1[:,direction] + 1e-6
        x2[:,direction] = x2[:,direction] - 1e-6

        probability_grad = (posterior_probability(x1, comp_mean_comp_cov) - posterior_probability(x2, comp_mean_comp_cov))/2e-6
        return {"probability grad": probability_grad}

    ###########################################################################
    def _int_gauss(self,S):
        return ((2.0*np.pi)**(len(S)/2.0))*np.sqrt(np.linalg.det(S))

    ##################################################################################
    ##################################################################################
    ##################################################################################
    ##################################################################################
    ######################Kernels#####################################################
    ##################################################################################
    ##################################################################################
    def squared_exponential_kernel(self, distance, length):
        """
        function for the squared exponential kernel

        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """
        kernel = torch.exp(-(distance ** 2) / (2.0 * (length ** 2)))
        return kernel


    def squared_exponential_kernel_robust(self, distance, phi):
        """
        function for the squared exponential kernel, This is the robust version, which means it is defined on [-infty,infty]
        instead of the usual (0,infty]

        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """
        kernel = np.exp(-(distance ** 2) * (phi ** 2))
        return kernel



    def exponential_kernel(self, distance, length):
        """
        function for the exponential kernel

        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """

        kernel = torch.exp(-(distance) / (length))
        return kernel

    def exponential_kernel_robust(self, distance, phi):
        """
        function for the exponential kernel, This is the robust version, which means it is defined on [-infty,infty]
        instead of the usual (0,infty]


        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """

        kernel = torch.exp(-(distance) * (phi**2))
        return kernel



    def matern_kernel_diff1(self, distance, length):
        """
        function for the matern kernel  1. order differentiability

        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """

        kernel = (1.0 + ((np.sqrt(3.0) * distance) / (length))) * torch.exp(
            -(np.sqrt(3.0) * distance) / length
        )
        return kernel


    def matern_kernel_diff1_robust(self, distance, phi):
        """
        function for the matern kernel  1. order differentiability, This is the robust version, which means it is defined on [-infty,infty]
        instead of the usual (0,infty]


        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """
        ##1/l --> phi**2
        kernel = (1.0 + ((np.sqrt(3.0) * distance) * (phi**2))) * torch.exp(
            -(np.sqrt(3.0) * distance) * (phi**2))
        return kernel



    def matern_kernel_diff2(self, distance, length):
        """
        function for the matern kernel  2. order differentiability

        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """

        kernel = (
            1.0
            + ((np.sqrt(5.0) * distance) / (length))
            + ((5.0 * distance ** 2) / (3.0 * length ** 2))
        ) * torch.exp(-(np.sqrt(5.0) * distance) / length)
        return kernel


    def matern_kernel_diff2_robust(self, distance, length):
        """
        function for the matern kernel  2. order differentiability, This is the robust version, which means it is defined on [-infty,infty]
        instead of the usual (0,infty]


        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            length (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """

        kernel = (
            1.0
            + ((np.sqrt(5.0) * distance) * (phi**2))
            + ((5.0 * distance ** 2) * (3.0 * phi ** 4))
        ) * np.exp(-(np.sqrt(5.0) * distance) * (phi**2))
        return kernel

    def sparse_kernel(self, distance, radius):
        """
        function for the sparse kernel
        this kernel is compactly supported, which makes the covariance matrix sparse

        Parameters:
        -----------
            distance (float): scalar or numpy array with distances
            radius (float):   length scale (note: set to one if length scales are accounted for by the distance matrix)
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """

        d = np.array(distance)
        d[d == 0.0] = 10e-6
        d[d > radius] = radius
        kernel = (np.sqrt(2.0)/(3.0*np.sqrt(np.pi)))*\
        ((3.0*(d/radius)**2*np.log((d/radius)/(1+np.sqrt(1.0 - (d/radius)**2))))+\
        ((2.0*(d/radius)**2+1.0)*np.sqrt(1.0-(d/radius)**2)))
        return kernel

    def periodic_kernel(self, distance, length, p):
        """periodic kernel
        Parameters:
        -----------
            distance: float or array containing distances
            length (float): the length scale
            p (float): period of the oscillation
        Return:
        -------
            a structure of the she shape of the distance input parameter
        """
        kernel = np.exp(-(2.0/length**2)*(np.sin(np.pi*distance/p)**2))
        return kernel

    def linear_kernel(self, x1,x2, hp1,hp2,hp3):
        """
        function for the linear kernel in 1d

        Parameters:
        -----------
            x1 (float):  scalar position of point 1
            x2 (float):  scalar position of point 2
            hp1 (float): vertical offset of the linear kernel
            hp2 (float): slope of the linear kernel
            hp3 (float): horizontal offset of the linear kernel
        Return:
        -------
            scalar
        """
        kernel = hp1 + (hp2*(x1-hp3)*(x2-hp3))
        return kernel

    def dot_product_kernel(self, x1,x2,hp,matrix):
        """
        function for the dot-product kernel

        Parameters:
        -----------
            x1 (2d numpy array of points):  scalar position of point 1
            x2 (2d numpy array of points):  scalar position of point 2
            hp (float):                     vertical offset
            matrix (2d array of len(x1)):   a metric tensor to define the dot product
        Return:
        -------
            numpy array of shape len(x1) x len(x2)
        """
        kernel = hp + x1.T @ matrix @ x2
        return kernel

    def polynomial_kernel(self, x1, x2, p):
        """
        function for the polynomial kernel

        Parameters:
        -----------
            x1 (2d numpy array of points):  scalar position of point 1
            x2 (2d numpy array of points):  scalar position of point 2
            p (float):                      exponent
        Return:
        -------
            numpy array of shape len(x1) x len(x2)
        """
        kernel = (1.0+x1.T @ x2)**p
        return p

    def get_distance_matrix_robust(self,x1,x2,hps):
        d = torch.zeros(size = (len(x1),len(x2)), dtype = float)
        for i in range(x1.shape[1]):
            d += ((x1[:,i].reshape(-1, 1) - x2[:,i])*hps[i+1])**2
        return torch.sqrt(d + 1e-16)

    def default_kernel(self,x1,x2,hyperparameters,obj):
        ################################################################
        ###standard anisotropic kernel in an input space with l2########
        ################################################################
        """
        x1: 2d numpy array of points
        x2: 2d numpy array of points
        obj: object containing kernel definition

        Return:
        -------
        Kernel Matrix
        """
        distance_matrix = self.get_distance_matrix_robust(x1,x2,hyperparameters)
        #return   hyperparameters[0]**2 *  obj.matern_kernel_diff1(distance_matrix,1)
        return hyperparameters[0]**2  *  torch.exp(-distance_matrix)

    def d_gp_kernel_dx(self, points1, points2, direction, hyperparameters):
        new_points = np.array(points1)
        epsilon = 1e-6
        new_points[:,direction] += epsilon
        a = self.kernel(new_points, points2, hyperparameters,self)
        b = self.kernel(points1,    points2, hyperparameters,self)
        derivative = ( a - b )/epsilon
        return derivative

    def d_gp_kernel_dh(self, points1, points2, direction, hyperparameters):
        new_hyperparameters1 = np.array(hyperparameters)
        new_hyperparameters2 = np.array(hyperparameters)
        epsilon = 1e-6
        new_hyperparameters1[direction] += epsilon
        new_hyperparameters2[direction] -= epsilon
        a = self.kernel(points1, points2, new_hyperparameters1,self)
        b = self.kernel(points1, points2, new_hyperparameters2,self)
        derivative = ( a - b )/(2.0*epsilon)
        return derivative

    def gp_kernel_gradient(self, points1, points2, hyperparameters):
        gradient = np.empty((len(hyperparameters), len(points1),len(points2)))
        for direction in range(len(hyperparameters)):
            gradient[direction] = self.d_gp_kernel_dh(points1, points2, direction, hyperparameters)
        return gradient

    def kernel_auto(self,hps):
        return self.kernel(self.x_data, self.x_data, hps, self)


    def gp_kernel_gradient_auto(self, hyperparameters):
        hps = hyperparameters.detach().clone()
        #hps = torch.tensor([2.3,4.5,3.2], requires_grad = True)
        hps.requires_grad = True
        #m = partial(self.kernel, self.x_data, self.x_data, obj = self)
        #grad = torch.autograd.functional.jacobian(m,hp)
        y = self.kernel_auto(hps)
        #print(y)
        y.backward(torch.eye((100)))
        grad = hps.grad
        #v = torch.zeros(len(hyperparameters), dtype = float)
        return grad

    def gp_kernel_derivative(self, points1, points2, direction, hyperparameters):
        #gradient = np.empty((len(hyperparameters), len(points1),len(points2)))
        derivative = self.d_gp_kernel_dh(points1, points2, direction, hyperparameters)
        return derivative

    def d2_gp_kernel_dh2(self, points1, points2, direction1, direction2, hyperparameters):
        ###things to consider when things go south with the Hessian:
        ###make sure the epsilon is appropriate, not too large, not too small, 1e-3 seems alright
        epsilon = 1e-3
        new_hyperparameters1 = np.array(hyperparameters)
        new_hyperparameters2 = np.array(hyperparameters)
        new_hyperparameters3 = np.array(hyperparameters)
        new_hyperparameters4 = np.array(hyperparameters)

        new_hyperparameters1[direction1] = new_hyperparameters1[direction1] + epsilon
        new_hyperparameters1[direction2] = new_hyperparameters1[direction2] + epsilon

        new_hyperparameters2[direction1] = new_hyperparameters2[direction1] + epsilon
        new_hyperparameters2[direction2] = new_hyperparameters2[direction2] - epsilon

        new_hyperparameters3[direction1] = new_hyperparameters3[direction1] - epsilon
        new_hyperparameters3[direction2] = new_hyperparameters3[direction2] + epsilon

        new_hyperparameters4[direction1] = new_hyperparameters4[direction1] - epsilon
        new_hyperparameters4[direction2] = new_hyperparameters4[direction2] - epsilon

        return (self.kernel(points1,points2,new_hyperparameters1,self) \
              - self.kernel(points1,points2,new_hyperparameters2,self) \
              - self.kernel(points1,points2,new_hyperparameters3,self) \
              + self.kernel(points1,points2,new_hyperparameters4,self))\
              / (4.0*(epsilon**2))
#    @profile
    def hessian_gp_kernel(self, points1, points2, hyperparameters):
        hessian = np.zeros((len(hyperparameters),len(hyperparameters), len(points1),len(points2)))
        for i in range(len(hyperparameters)):
            for j in range(i+1):
                hessian[i,j] = hessian[j,i] = self.d2_gp_kernel_dh2(points1, points2, i,j, hyperparameters)
        return hessian

    def dm_dh(self,hps):
        gr = torch.empty((len(hps),len(self.x_data)), dtype = float)
        for i in range(len(hps)):
            temp_hps1 = hps.detach().clone()
            temp_hps1[i] = temp_hps1[i] + 1e-6
            temp_hps2 = hps.detach().clone()
            temp_hps2[i] = temp_hps2[i] - 1e-6
            a = self.mean_function(self,self.x_data,temp_hps1)
            b = self.mean_function(self,self.x_data,temp_hps2)
            gr[i] = (a-b)/2e-6
        return gr
    ##########################
    def d2m_dh2(self,hps):
        hess = np.empty((len(hps),len(hps),len(self.x_data)))
        e = 1e-4
        for i in range(len(hps)):
            for j in range(i+1):
                temp_hps1 = np.array(hps)
                temp_hps2 = np.array(hps)
                temp_hps3 = np.array(hps)
                temp_hps4 = np.array(hps)
                temp_hps1[i] = temp_hps1[i] + e
                temp_hps1[j] = temp_hps1[j] + e

                temp_hps2[i] = temp_hps2[i] - e
                temp_hps2[j] = temp_hps2[j] - e

                temp_hps3[i] = temp_hps3[i] + e
                temp_hps3[j] = temp_hps3[j] - e

                temp_hps4[i] = temp_hps4[i] - e
                temp_hps4[j] = temp_hps4[j] + e


                a = self.mean_function(self,self.x_data,temp_hps1)
                b = self.mean_function(self,self.x_data,temp_hps2)
                c = self.mean_function(self,self.x_data,temp_hps3)
                d = self.mean_function(self,self.x_data,temp_hps4)
                hess[i,j] = hess[j,i] = (a - c - d + b)/(4.*e*e)
        return hess

    def d2f_dx2(self,hps,func):
        hess = np.empty((len(hps),len(hps)))
        e = 1e-4
        for i in range(len(hps)):
            for j in range(i+1):
                temp_hps1 = np.array(hps)
                temp_hps2 = np.array(hps)
                temp_hps3 = np.array(hps)
                temp_hps4 = np.array(hps)
                temp_hps1[i] = temp_hps1[i] + e
                temp_hps1[j] = temp_hps1[j] + e

                temp_hps2[i] = temp_hps2[i] - e
                temp_hps2[j] = temp_hps2[j] - e

                temp_hps3[i] = temp_hps3[i] + e
                temp_hps3[j] = temp_hps3[j] - e

                temp_hps4[i] = temp_hps4[i] - e
                temp_hps4[j] = temp_hps4[j] + e


                a = func(temp_hps1)
                b = func(temp_hps2)
                c = func(temp_hps3)
                d = func(temp_hps4)
                hess[i,j] = hess[j,i] = (a - c - d + b)/(4.*e*e)
        return hess

    def df_dx(self,hps,func):
        grad = np.empty((len(hps)))
        e = 1e-6
        for i in range(len(hps)):
            temp_hps1 = np.array(hps)
            temp_hps2 = np.array(hps)
            temp_hps1[i] = temp_hps1[i] + e
            temp_hps2[i] = temp_hps2[i] - e

            a = func(temp_hps1)
            b = func(temp_hps2)
            grad[i] = (a - b)/(2.*e)
        return grad

    ################################################################
    def _normalize_y_data(self):
        mini = torch.min(self.y_data)
        self.y_data = self.y_data - mini
        maxi = torch.max(self.y_data)
        self.y_data = self.y_data / maxi




