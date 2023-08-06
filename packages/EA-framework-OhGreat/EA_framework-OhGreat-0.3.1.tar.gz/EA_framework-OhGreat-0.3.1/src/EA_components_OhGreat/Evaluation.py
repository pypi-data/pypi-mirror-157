import numpy as np
from EA_components_OhGreat.Population import Population


class Ackley():
    """ Evaluate a solution on Ackley problem
        Minimization problem. Optimum is 0.
    """
    def __init__(self, a = 20, b = 0.2, c = 2*np.pi, minimize=True):
        self.a = a
        self.b = b
        self.c = c
        self.optimum = 0
        
    def __call__(self, X: Population):
        ret_vals = []
        x = X.individuals
        for ind_idx in range(X.individuals.shape[0]):
            dim = x.shape[1]
            term1 = -1. * self.a * np.exp(-1. * self.b * np.sqrt((1./dim) * sum(map(lambda i: i**2, x[ind_idx]))))
            term2 = -1. * np.exp((1./dim) * (sum(map(lambda j: np.cos(self.c * j), x[ind_idx]))))
            y = term1 + term2 + self.a + np.exp(1)
            ret_vals.append(y)
        X.fitnesses =  np.array(ret_vals)


class Rastrigin():
    """ Evaluate a solution on Rastringin problem.
        Minimization problem. Optimum is 0.
    """
    def __init__(self, a = 10, minimize=True):
        self.a = a
        self.optimum = 0
        
    def __call__(self, X: Population):
        ret_vals = []
        x = X.individuals
        for ind_idx in range(X.individuals.shape[0]):
            y = self.a * x.shape[1] + sum(map(lambda i: i**2 - self.a * np.cos(2*np.pi*i), x[ind_idx]))
            ret_vals.append(y)
        X.fitnesses =  np.array(ret_vals)


class Thevenot():
    """ Evaluate a solution on Thevenot problem.
        Minimization problem. Optimum is 0, for m=5 and beta=15
    """
    def __init__(self, m=5, beta=15):
        self.m = m
        self.beta = beta

    def __call__(self, X: Population):
        ret_vals = []
        x = X.individuals
        for ind_idx in range(X.individuals.shape[0]):
            res = np.exp(-np.sum((x[ind_idx]/self.beta)**(2*self.m)))
            res = res - 2*np.exp(-np.prod(x[ind_idx]**2))*np.prod(np.cos(x[ind_idx])**2)
            ret_vals.append(res)
        X.fitnesses =  np.array(ret_vals)


class Adjiman():
    """ Evaluate a solution on Adjimin problem.
        Minimization problem. Optimum is -2.02181.
    """
    def __call__(self, X: Population):
        ret_vals = []
        x = X.individuals
        for ind_idx in range(X.individuals.shape[0]):
            res = np.sum(np.cos(x[ind_idx]) * np.sin(x[ind_idx]) - x[ind_idx] / (x[ind_idx]**2 + 1))
            ret_vals.append(res)
        X.fitnesses =  np.array(ret_vals)


class Bartels():
    """ Evaluate a solution on Bartels problem.
        Minimization problem. Optimum is 1.
    """
    def __call__(self, X: Population):
        ret_vals = []
        y = X.individuals
        for ind_idx in range(X.individuals.shape[0]):
            x = y[ind_idx]
            res = np.sum(np.abs(x**2 + x**2 + x*x) + np.abs(np.sin(x)) + np.abs(np.cos(x)))
            ret_vals.append(res)
        X.fitnesses =  np.array(ret_vals)