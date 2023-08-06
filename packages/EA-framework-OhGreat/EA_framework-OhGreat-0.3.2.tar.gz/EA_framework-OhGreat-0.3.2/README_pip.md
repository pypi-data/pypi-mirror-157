# Evolutionary Algorithms Framework
## *Documentation under work*

This repository contains a framework for applying evolutionary strategies (ES) on arbitrary black box optimization problems. The original github repository can be found <a href="https://github.com/OhGreat/evolutionary_algorithms">here</a>.

## Usage

### Population class
The population class contains the individuals that are optimized with the EA.
To initialize a population you can use the following commands:
```python
from EA_components.Population import Population
population = Population(pop_size, ind_size, mutation)
```
where:
- `pop_size` : is an integer value representing the size of the population
- `ind_size` : integer value representing the size of an individual. Can be seen as the problem dimension.
- `mutation` : Mutation type. It is used to initialize sigmas and alphas. Please consult the mutation section to learn more about how to initialize a mutation.

Attributes of the class:
- *the parameters specified above*
- `individuals`: numpy array of shape (pop_size, ind_size), represents the population's values/solutions.
- `sigmas`: sigma values used in mutation for the *IndividualSigma* mutation.

Methods available:
- `sigma_init`: initializes or resets sigmas, with respect to the mutation defined.
- `max_fitness`: returns the maximum fitness and the index i nthe population.
- `min_fitness`: returns the minimum fitness and the index in the population.
- `best_fitness`: takes as argument a boolean value *minimize*, which is True by default and defines if the problem is minimization.

example usage of methods:
```python
# sigma_init happens inplace, no return value
population.sigma_init()  
# max_fitness returns max value and index
max_fit, max_fit_idx = population.max_fitness()
# min_fitness returns min value and index
min_fit, min_fit_idx = population.min_fitness()
# best_fitness uses the above functions depending on minimize parameter
best_fit, best_fit_idx = population.best_fitness(minimize=True)
```

### Recombination
All the recombinations created are applied *inplace* on the offspring populations and there is no return value. The following Recombination classes have been implemented: ***Intermediate***, ***GlobalIntermediary***, ***Discrete***, ***GlobalDiscrete***. All the recombinations take as input the parent and offspring population. The offspring population is used to save the new individuals created and specifies the size of the offspring population. Using the recombinations can be done as in the example below:
```python
from EA_components.Recombination import Intermediate
recomb = Intermediate()
recomb(parents, offsprings)
```

### Mutation

### Selection

### Evaluation

### EA

## Full algorithm example