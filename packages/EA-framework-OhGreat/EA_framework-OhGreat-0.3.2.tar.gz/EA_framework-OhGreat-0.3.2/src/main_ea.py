from EA_components_OhGreat.Population import *
from EA_components_OhGreat.Recombination import *
from EA_components_OhGreat.Mutation import *
from EA_components_OhGreat.Selection import *
from EA_components_OhGreat.Evaluation import *
from EA_components_OhGreat.EA import *
import matplotlib.pyplot as plt
import argparse
import time
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', action='store',
                        dest='recombination', type=str,
                        default=None,
                        help="Defines the recombination strategy.")
    parser.add_argument('-m', action='store',
                        dest='mutation', type=str,
                        default='IndividualSigma',
                        help="Defines the mutation strategy.")
    parser.add_argument('-s', action='store',
                        dest='selection', type=str,
                        default='PlusSelection',
                        help="Defines the selection strategy.")
    parser.add_argument('-e', action='store',
                        dest='evaluation', type=str,
                        nargs='+', default=[Ackley(),
                                            Rastrigin(), 
                                            Bartels()],
                        help="Defines the evaluation function.")
    parser.add_argument('-min', action='store_true', 
                        dest='minimize',
                        help="Use this flag if the problem is minimization.")
    parser.add_argument('-ps', action='store',
                        dest='parents_size', type=int,
                        default=4,
                        help="Defines the number of parents per generation.")
    parser.add_argument('-os', action='store',
                        dest='offspring_size', type=int,
                        default=24,
                        help="Defines the number of offspring per generation.")
    parser.add_argument('-pd', action='store',
                        dest='problem_dimension', type=int,
                        default=5,
                        help="Defines the problem dimension which is also the size of each individual.")
    parser.add_argument('-pat', action='store',
                        dest='patience', type=int,
                        default=None,
                        help="Defines the wait time before resetting sigmas.")          
    parser.add_argument('-b', action='store',
                        dest='budget', type=int,
                        default=10000,
                        help="Defines the total amount of evaluations.")
    parser.add_argument('-rep', action='store',
                        dest='repetitions', type=int,
                        default=100,
                        help="Defines the number of repetitions to average results.")
    parser.add_argument('-save_plots', action='store_true', 
                        help="Use this flag to save evaluation function plots.")
    parser.add_argument('-v', action='store',
                        dest='verbose', type=int,
                        default=1,
                        help="Defines the intensity of debug prints.")
    parser.add_argument('-seed', action='store',
                        dest='seed', type=int,
                        default=None,
                        help="Defines the seed for result reproducibility.")
    args = parser.parse_args()
    print("Arguments passed:")
    print(args)

    # define arguments here to be able to make checks later
    minimize = args.minimize
    budget = args.budget
    patience = args.patience
    parents_size = args.parents_size
    offspring_size = args.offspring_size
    individual_size = args.problem_dimension

    # recombination specific control
    if args.recombination != None:
        recombination = globals()[args.recombination]()
    # GlobalIntermediary recombination check
    elif args.recombination == "GlobalIntermediary" and args.offspring_size > 1:
        print("GlobalIntermediary recombination cannot be used with more than one offspring.")
        print("Please use a valid configuration")
        exit()
    else: recombination = None

    # mutation specific controls
    mutation = globals()[args.mutation]()
    
    # selection specific controls
    selection=globals()[args.selection]()

    # evaluation function specific controls
    evaluation=[globals()[curr_eval]() for curr_eval in args.evaluation ]

    # extra parameters
    verbose=args.verbose
    if args.seed != None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # iterate over chosen evaluation functions
    for eval_fun in evaluation:

        # Repeat experiment for n = 'repetitions' times
        best_evals = []
        all_evals = []
        repetitions = args.repetitions
        start_time = time.time()
        for _ in range(repetitions):
            # define Evolutionary Algorithm
            ea = EA(minimize=minimize,
                    budget=budget,
                    patience=patience,
                    parents_size=parents_size,
                    offspring_size=offspring_size,
                    individual_size=individual_size,
                    recombination=recombination,
                    mutation=mutation,
                    selection=selection,
                    evaluation=eval_fun,
                    verbose=verbose)
            # run the ea strategy
            _, all_evals_for_rep = ea.run()
            # keep track of results
            if minimize:
                best_evals.append(np.min(all_evals_for_rep))
            else: best_evals.append(np.max(all_evals_for_rep))
            all_evals.append(all_evals_for_rep)
        end_time = time.time()

        # print results for current evaluation function
        best = np.min(best_evals) if minimize else np.max(best_evals)
        print(f"best_eval: {best}, mean eval: {np.round(np.mean(best_evals),4)}")
        print(f"{eval_fun.__class__.__name__} - run time: {np.round(end_time - start_time, 2)} for {repetitions} repetitions.")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # save plot of current problem evaluations
        if args.save_plots:
            save_plot(eval_fun.__class__.__name__, np.array(all_evals))

def save_plot(plot_name, data):
    """ Save plot of the performance of the algorithm
        for current evaluation function.
    """
    # create directory for plots and save plot
    if not os.path.exists('plots'):
        os.makedirs('plots')

    plt.clf() # clear past figures
    plt.plot(data.mean(axis=0), label=plot_name)
    plt.fill_between(np.arange(data.shape[1]),data.min(axis=0), 
                                data.max(axis=0),alpha=0.2)
    plt.xlabel("budget")
    plt.ylabel("evaluation")
    plt.title(plot_name)
    plt.savefig('plots/'+plot_name)

if __name__ == "__main__":
    main()