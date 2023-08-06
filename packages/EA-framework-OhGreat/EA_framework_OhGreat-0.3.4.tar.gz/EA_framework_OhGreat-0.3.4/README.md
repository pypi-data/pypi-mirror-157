# Evolutionary Algorithms Framework

This repository contains a framework for applying evolutionary algorithms (EA) on arbitrary black box optimization problems. The purpose of this package is to facilitate the experimentation of EA in various settings. An example usage of this repository can be found <a href="https://github.com/OhGreat/es_for_rl_experimentation">here</a>, where the framework is applied in a reinforcement learning setting to solve gym environments.

<!-- TABLE OF CONTENTS -->
<details id="test">
  <summary>Table of Contents</summary>
  <ul>
    <li><a href="#implementation">Implementation</a></li>
    <li><a href="#installing">Installing</a></li>
    <li><a href="#usage">Usage of repository</a></li>
    <ul>
    <li><a href="#usage-of-the-cloned-repository">Usage of repository</a></li>
    <li><a href="#usage-of-the-pip-package">Usage of the pip package</a></li>
    <li><a href="#creating-your-own-evaluation-functions">Creating your own evaluation function</a></li>
    </ul>
    <li><a href="#examples">Examples</a></li>
    <li><a href="#issues">Issues</a></li>
    <li><a href="#future-work">Future Work</a></li>
  </ul>
</details>

## Implementation

The following ES steps have been implemented:
 - **Recombination**: *Intermediate*, *GlobalIntermediary*, *Discrete*, *GlobalDiscrete*
 - **Mutation**: *IndividualSigma*, *(CMA to be added)*
 - **Selection**: (μ + λ) - *PlusSelection*, (μ , λ) - *CommaSelection*
<br/><br/>

The following optimization problems have been implemented:<br/>
**Ackley**, **Adjiman**, **Rastrigin**, **Thevenot**, **Bartels**


## Installing
The various EA components present in the `src/EA_components` directory, have been encapsuled for convenience in a pip package that can be installed via the following command:
```
pip install EA-framework-OhGreat==0.3.4
```
Instrutions and documentation on how to use this package are available <a href="https://pypi.org/project/EA-framework-OhGreat/">here</a>.

To clone and use the repository instead, `Python 3` environment is required, with the packages found in the `requirements.txt` file in the main directory. To install them, run from `main directory` the following command:
```
pip install -r requirements.txt
```

## Usage

### Usage of cloned repository
The main file to run experiments is the `main_es.py` file in the `src` directory. A detailed description of all the configurable parameters is available below. Example shell scripts have also been created as an example to set arguments, under the `scripts` directory.

The following arguments can be set when running `main_es.py`:
- `-r` : defines the recombination type. Available options: *"Intermediate"*, *"GlobalIntermediary"*, *"Discrete"*, *"GlobalDiscrete"*.
- `-m` : defines the mutation type. Available options: *"IndividualSigma"*, *"IndividualOneFifth"*.
- `-s` : defines the selection type. Available options: *"PlusSelection"*, *"CommaSelection"*.
- `-e` : defines the evaluation type. Available options: *"Rastrigin"*, *"Ackley"*, *"Thevenot"*, *"Adjiman"*, *"Bartels"*. If an evaluation function is not defined, all the above functions will be used.
- `-min` : set this flag if the optimization problem is minimization.
- `-ps` : defines the number of parents. Should be an integer value.
- `-os` : defines the number of offsprings. Should be an integer value.
- `-pd` : defines the problem dimension. Will be used to set the individual size.
- `-pat` : defines the number of unsuccesful generations to wait before resetting sigmas.
- `-b` : defines the budget. Should be an integer value.
- `-rep` : defines the number of repetitions to average results. Should be an integer value.
- `-v` : defines the verbose (prints) intensity. Available options are: *0*, *1*, *2* ,with *2* being the most intense. 
- `-seed` : defines the seed to use for reproducibility of results. Set to an integer value.
- `-save_plots` : set the flag in order to save plots of the algorithms performance.

### Usage of pip package
To use the pip package please refer to the documentation available <a href="https://pypi.org/project/EA-framework-OhGreat/">here</a>.

### Creating your own evaluation functions 
To create your own evaluation function you can extend the `Evaluate` class on the `Evaluation.py` file in the `src/classes` folder. Each evaluation class should have at least the __call__ methods defined to work properly.

## Examples 
The following image is the result of the `individual.sh` configuration found in the `src/scripts` directory.

<img src="https://github.com/OhGreat/evolutionary_algorithms/blob/main/readme_aux/example_plots.png" />

## Issues
If you encounter any problems while using the framework you can notify me by opening an issue here:
https://github.com/OhGreat/evolutionary_algorithms/issues

## Future Work
- ~~add more optimization problems~~
- ~~implement more recombination types~~
- implement CMA-ES mutation strategy
- implement upsampling