from EA_components_OhGreat.Population import *
from EA_components_OhGreat.Recombination import *
from EA_components_OhGreat.Mutation import *
from EA_components_OhGreat.Selection import *
from EA_components_OhGreat.Evaluation import *
from EA_components_OhGreat.EA import *
import time
from copy import deepcopy
import multiprocessing as mp

def main():
    test_iters = 2000

    parents_size = 10
    offspring_size = 30
    individual_size = 20000

    mutation = IndividualSigma()

    parents = Population(parents_size,
                        individual_size,
                        mutation)
    offspring = Population(offspring_size, 
                            individual_size, 
                            mutation)
    # print(offspring.individuals)

    parallel_offs  = [Population(1,individual_size, mutation) 
                        for _ in range(offspring_size)]
    print(parallel_offs[0].individuals)
    # print()

    # no parallel loop
    t_start = time.time()
    for _ in range(test_iters):
        mutation(offspring)
    t_end = time.time()

    # print(offspring.individuals)
    print(f"No parallelization time: {np.round(t_end - t_start,3)}")

    # parallel execution
    t_start = time.time()
    pool = mp.Pool(mp.cpu_count())
    for _ in range(test_iters):
        for i in range(len(parallel_offs)):
            pool.apply_async(mutation, args=parallel_offs[i])
    pool.close()
    pool.join()
    t_end = time.time()
    print(parallel_offs[0].individuals)
    print(f"Parallelization time: {np.round(t_end - t_start,3)}")


def get_result(result):
    global results
    results.append(result)

if __name__ == "__main__":
    main()