from EA_components_OhGreat.Population import *
import numpy as np
import random


class Recombination:
    def __call__(self):
        pass


class Intermediate(Recombination):
    """ Creates offspring by taking the average values of the parents
    """
    def __call__(self, parents: Population, offspring: Population):
        for i in range(offspring.pop_size):
            # pick two parents at random
            p1, p2 = random.sample(range(parents.pop_size), k=2)
            # update offspring population
            offspring.individuals[i] = (parents.individuals[p1] + parents.individuals[p2]) / 2
            offspring.sigmas[i] = (parents.sigmas[p1] + parents.sigmas[p2]) / 2
            # recombine alphas if we are using them
            if parents.mutation.__class__.__name__ == "Correlated":
                offspring.alphas[i] = (parents.alphas[p1] + parents.alphas[p2]) / 2


class GlobalIntermediary(Recombination):
    """ Generates one offspring as the mean value of all the parents.
    """
    def __call__(self, parents: Population, offspring: Population):
        offspring.individuals = parents.individuals.mean(axis=0, keepdims=True)
        offspring.sigmas = parents.sigmas.mean(axis=0)
        if parents.mutation.__class__.__name__ == "Correlated":
                offspring.alphas = parents.alphas.mean(axis=0, keepdims=True)


class Discrete(Recombination):
    """ Creates discretely recombined offsprings.
    """
    def __call__(self, parents: Population, offspring: Population):
        # reset offspring values
        offspring.individuals = []
        offspring.sigmas = []
        # create rng for each element of every new individual
        elem_rng = np.random.uniform(size=(offspring.pop_size,offspring.ind_size))
        for i in range(offspring.pop_size):
            # sample parent individuals
            p1, p2 = random.sample(range(parents.pop_size), k=2)
            # create new individual
            offspring.individuals.append([par_1 if p >= .5 else par_2
                                        for par_1, par_2, p in 
                                        zip(parents.individuals[p1],
                                            parents.individuals[p2],
                                            elem_rng[i])])
            # create new sigmas
            offspring.sigmas.append([par_1 if p >= .5 else par_2
                                    for par_1, par_2, p in 
                                    zip(parents.sigmas[p1],
                                        parents.sigmas[p2],
                                        elem_rng[i])])
        # revert back to numpy
        offspring.individuals = np.array(offspring.individuals)
        offspring.sigmas = np.array(offspring.sigmas)


class GlobalDiscrete(Recombination):
    """ Creates discrete recombined offsprings.
    """
    def __call__(self, parents: Population, offspring: Population):
        # rng
        parent_choices = np.random.choice(range(parents.pop_size), size=(offspring.pop_size, offspring.ind_size))
        # reset offspring
        offspring.individuals = []
        offspring.sigmas = []
        for i in range(offspring.pop_size):
            # create new offspring
            offspring.individuals.append([curr_par[curr_choice] 
                                            for curr_par, curr_choice in 
                                            zip(parents.individuals.T, 
                                                parent_choices[i])])
            # create offspring's sigmas
            offspring.sigmas.append([curr_par[curr_choice] 
                                            for curr_par, curr_choice in 
                                            zip(parents.sigmas.T, 
                                                parent_choices[i])])
        # revert arrays to numpy
        offspring.individuals = np.array(offspring.individuals)
        offspring.sigmas = np.array(offspring.sigmas)
