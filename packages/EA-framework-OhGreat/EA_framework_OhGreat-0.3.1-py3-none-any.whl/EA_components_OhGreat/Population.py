import numpy as np


class Population:
    """ Attributes:
            - pop_size : size of population
            - ind_size : size of the individual
            - individuals: 'weights' of the individual that get tuned by the algorithm
            - fitness: defines how good the current individual is for the problem.
            - mutation : defines the mutation to be used in order to initialize parameters
            - sigmas : parameters used for the Individual Mutation
    """
    def __init__(self, pop_size, ind_size, mutation):
        self.mutation = mutation
        self.pop_size = pop_size
        self.ind_size = ind_size
        self.fitnesses = np.array([])
        # initialize individual values
        self.individuals = np.random.uniform(0, 1, size=(self.pop_size, self.ind_size))
        # initialize sigmas
        self.sigma_init()

    def sigma_init(self):
        """ Initialize sigma values depending on the mutation.
        """
        if self.mutation.__class__.__name__ == "OneSigma":
            self.sigmas = np.random.uniform(max(0, np.min(self.individuals)/6), 
                                            np.max(self.individuals)/6, 
                                            size=self.pop_size)
        else:
            self.sigmas = np.random.uniform(max(0, np.min(self.individuals)/6), 
                                            np.max(self.individuals)/6, 
                                            size=(self.pop_size, self.ind_size))

    def max_fitness(self):
        """ Return the maximum fitness and its index.
        """
        arg_max = np.argmax(self.fitnesses)
        return self.fitnesses[arg_max], arg_max 

    def min_fitness(self):
        """ Return the minimum fitness and its index.
        """
        arg_min = np.argmin(self.fitnesses)
        return self.fitnesses[arg_min], arg_min

    def best_fitness(self, minimize=True):
        """ Returns the best fitness and index of fittest individual.
            
            Params:
                - minimize: set to True for minimization optimization
        """
        if minimize:
            arg_max = np.argmax(self.fitnesses)
            return self.fitnesses[arg_max], arg_max 
        else:
            arg_min = np.argmin(self.fitnesses)
            return self.fitnesses[arg_min], arg_min
