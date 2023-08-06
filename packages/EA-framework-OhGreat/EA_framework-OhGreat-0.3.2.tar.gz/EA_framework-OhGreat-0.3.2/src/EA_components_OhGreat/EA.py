from EA_components_OhGreat .Population import *
import numpy as np


class EA:
    """ Main Evolutionary Strategy class
    """
    def __init__(self, minimize, budget, patience,
                parents_size, offspring_size,
                individual_size,
                recombination, mutation, 
                selection, evaluation,
                verbose):
        self.minimize = minimize
        self.budget = budget
        self.patience = patience
        self.parents_size = parents_size
        self.offspring_size = offspring_size
        self.individual_size = individual_size
        self.recombination = recombination
        self.mutation = mutation
        self.selection = selection
        self.evaluation = evaluation
        self.verbose=verbose
        self.parents = Population(  self.parents_size,
                                    self.individual_size,
                                    mutation)
        self.offspring = Population(self.offspring_size, 
                                    self.individual_size, 
                                    mutation)

    def run(self):
        """ Runs the Evolutionary Strategy.
            Returns the best individual and the best fitness.
        """
        # Initialize budget and patience
        self.curr_budget, self.curr_patience = 0, 0
        # Initialize number of better generations found total generations
        self.better_generations = 0
        self.total_generations = 0
        # Initial parents setup
        self.evaluation(self.parents)
        self.best_eval, self.best_index = self.parents.best_fitness(self.minimize)
        self.best_indiv = self.parents.individuals[self.best_index]
        self.curr_budget += self.parents_size
        self.all_best_evals = []
        self.gen_count = 0

        while self.curr_budget < self.budget:
            # Recombination: creates new offspring
            if self.recombination is not None:
                self.recombination(self.parents, self.offspring)
            # Mutation: mutate offspring population
            self.mutation(self.offspring)
            # Evaluation: evaluate offspring population
            self.evaluation(self.offspring)
            # Selection: select the parents for the next geneation
            self.selection(self.parents, self.offspring, self.minimize)
            # Update control variables, e.g. budget and best individual
            self.update_control_vars()
        if self.verbose > 0: # prints once per run
                print(f"Best eval: {self.best_eval}")
        return self.best_indiv, np.array(self.all_best_evals)

    def update_control_vars(self):
        """ Updates all control variables
        """
        # Update the best individual
        # best individual is in the first position due to selection
        curr_best_eval = self.parents.fitnesses[0]
        self.all_best_evals.append(curr_best_eval)
        if (self.minimize and curr_best_eval < self.best_eval) \
             or curr_best_eval > self.best_eval:  # min or max new best conditions
            self.best_indiv = self.parents.individuals[0]
            self.best_eval = curr_best_eval
            # increment number of successful generations
            self.better_generations += 1
            # reset patience since we found a new best
            self.curr_patience = 0
            # debug print
            if self.verbose > 1: # prints every time the algorithm finds a new best
                print(f"Generation {self.gen_count} Best eval: {np.round(self.best_eval, 3)}, budget: {self.curr_budget}/{self.budget}")
        else:  # new best not found, increment current patience counter
            if self.verbose > 1:
                print(f"Generation {self.gen_count}, no new best found. Budget: {self.curr_budget}/{self.budget}")
            self.curr_patience += 1
        # increment past generations counter
        self.total_generations += 1
        # reset sigmas if patience has been defined
        if self.patience and self.curr_patience >= self.patience:
            if self.verbose > 1:
                print(f"~~Reinitializing sigmas for generation {self.gen_count}.~~")
            self.parents.sigma_init()
            self.curr_patience = 0
        
        # increment current budget
        self.curr_budget += self.offspring_size
        # increment generation counter
        self.gen_count += 1
