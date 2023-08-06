import numpy as np
from EA_components_OhGreat.Population import *


class Mutation:
    def mutate(self):
        """ Mutate the population.
        """
        pass

    def __call__(self, *args):
        self.mutate(*args)


class IndividualSigma(Mutation):
    """ Individual sigma method.
    """
    def mutate(self, population: Population):
        # define tau and tau'
        tau = 1/np.sqrt(2*(np.sqrt(population.ind_size)))
        tau_prime = 1/(np.sqrt(2*population.ind_size))
        # create N and N' matrixes
        normal_matr_prime = np.random.normal(0,tau_prime,(population.pop_size,1))
        normal_matr = np.random.normal(0,tau,(population.pop_size, population.ind_size))
        #update our sigmas
        population.sigmas = population.sigmas * np.exp(normal_matr + normal_matr_prime)
        # update our individuals
        if (population.sigmas < 0).any(): # make sure sigmas are positive
            print("Sigmas < 0! Trying a reset..", population.sigmas)
            population.sigma_init()
        # create noise and update population
        noises = np.random.normal(0,population.sigmas)
        population.individuals += noises

        
# TODO: complete algorithm
class Correlated(Mutation):
    def mutate(self, population: Population, minimize=True):
        # sort our values
        if minimize:
            sorted_ind = np.argsort(population.fitnesses)
        else:  # we need to reverse our indexes
            sorted_ind = np.argsort(population.fitnesses)[::-1]

        pass
