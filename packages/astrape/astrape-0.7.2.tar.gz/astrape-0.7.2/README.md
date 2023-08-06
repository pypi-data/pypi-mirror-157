# ASTRAPE : A STrategic, Reproducible & Accessible Project and Experiment



<div align="right">
      <b>Creator : Woosog Benjamin Chay</b> 
</div>
<div align="right">
      <b>benchay1@gmail.com (preferred) / benchay@kaist.ac.kr</b> 
</div>
<br/>
<br/>

<div align="center">
      <code><font size=4>pip install astrape</code>
</div>

<div align="center">
      <a href="https://astrape.readthedocs.io/en/latest/index.html">docs</a>
</div>

<div align="right">
      <a href="https://colab.research.google.com/drive/1VZCR84K2pzKpZoFGy3kp8vOZYAYyvQjJ?usp=sharing">colab tutorial (tutorial for 'Experiment')</a> <br/>
      <a href="https://github.com/benchay1999/astrape/blob/main/tutorial/project_tutorial.ipynb">tutorial.ipynb (tutorial for 'Project')</a>
</div>
      
**********

- [ASTRAPE : A STrategic, Reproducible & Accessible Project and Experiment](#astrape--a-strategic-reproducible--accessible-project-and-experiment)
- [1. Overview](#1-overview)
- [2. Project](#2-project)
  - [2-1. Visulaizing Data](#2-1-visulaizing-data)
  - [2-2. Creating *Experiment*s With Different Random Seeds](#2-2-creating-experiments-with-different-random-seeds)
  - [2-3. Set Models in Each Experiment](#2-3-set-models-in-each-experiment)
  - [2-4. Fit Models in Each Experiment](#2-4-fit-models-in-each-experiment)
  - [2-5. Save Fitted Models in Each Experiment](#2-5-save-fitted-models-in-each-experiment)
  - [2-6. Plot Results](#2-6-plot-results)
    - [2-6-1. Plot Performances With an Identical Model Type](#2-6-1-plot-performances-with-an-identical-model-type)
    - [2-6-2. Plot Performances With an Identical Model Structure](#2-6-2-plot-performances-with-an-identical-model-structure)
    - [2-6-3. Plot Performances of All Model Structures](#2-6-3-plot-performances-of-all-model-structures)
- [3. Experiment](#3-experiment)
  - [3-1. Specifying Models](#3-1-specifying-models)
  - [3-2. (Optional) Specifying Trainers](#3-2-optional-specifying-trainers)
  - [3-3. Fitting the Model](#3-3-fitting-the-model)
  - [3-4. Stacking Fitted Models](#3-4-stacking-fitted-models)
  - [3-5. Saving Models](#3-5-saving-models)
  - [3-6. Checking the Best Model Thus Far](#3-6-checking-the-best-model-thus-far)
  - [3-7. (Stratified) K-Fold Cross-Validation](#3-7-stratified-k-fold-cross-validation)
- [Miscellaneous](#miscellaneous)
  - [Setting Customized Pytorch-Lightning Models](#setting-customized-pytorch-lightning-models)
  - [](#)

**********
# 1. Overview
Astrape : [https://en.wikipedia.org/wiki/Astrape_and_Bronte](https://en.wikipedia.org/wiki/Astrape_and_Bronte)

Astrape is a package that would help you organize machine learning projects. It is written mostly in PyTorch Lightning([https://pytorchlightning.ai](https://pytorchlightning.ai)).
 


This project is motivated by the need to provide packages, of which only "human-language-like codings" are necessary, to whom that is not familiar with machine learning or with programming. Even though there are high-level machine learning frameworks such as PyTorch(and PyTorch-Lightning) or Tensorflow, it is difficult for beginners even to run a simple Perceptron due to the presence of magic commands e.g., codes regarding saving results, hyperparameter tuning, etc. Even if one has a strong background in learning theory, it would be a long journey to conduct an experiment when he/she hasn't acquired basic programming skills.

Astrape eliminated most of the low-level codings of the entire machine learning process so that every process in machine learning experiment can be done by typing nearly-human-level languages.

************
:zap: Astrape :zap: 


![Outline of Astrape](https://github.com/benchay1999/astrape/blob/main/astrape_outline.jpg?raw=true)


"Project" and "Experiment" conspire to the soul of Astrape. The term "Project" here refers to "all set of possible machine learning *experiments* for analyzing the given data". Wait, what is an *experiment* anyway? An *experiment* here means "a process of train/validation/test phase with certain random state acquired for all random operations such as splitting scheme, initialization scheme, etc.". "Experiment" is a collection of *experiments* with the same random state.

For stability's sake, you are tempted to (and should) conduct several "Experiments" with different random states to verify that your data analysis is indeed accurate. Astrape organizes such "Experiments" in a way that makes this sanity-checking process succinct and reproducible.



# 2. Project 

**Project** is defined as a set of *experiments*, with different random seed allocated to each *experiment*. It performs the A to Z of the process of a machine learning experiment.  

*Project* can visualize the data according to its type of domain e.g., image data, points.   

Check details in the [full tutorial](https://github.com/benchay1999/astrape/blob/main/tutorial/project_tutorial.ipynb).

![alt text](https://github.com/benchay1999/astrape/blob/main/tutorial/project.JPG?raw=true)


## 2-1. Visulaizing Data

You can visualize data using `.plot_data()` method. Depending on the domain of the data, such as image data or simple points in Euclidean space, `.plot_data()` automatically visulizes and saves the visualized figure. If the data is image data, you should specify the argument `domain_type` as `"image"`. Else if the data is points in Euclidean space, you should specify the argument `domain_type` as `"points"`. When the dimensionality of the points data is higher than 3, `.plot_data()` plots a 2D figure with 2 principal axes.

## 2-2. Creating *Experiment*s With Different Random Seeds

You can create *experiment*s with different random states using `.create_experiments()` method. Random seeds will be generated as per the `amount` of experiments you want to create.

![alt text](https://github.com/benchay1999/astrape/blob/main/tutorial/create_experiments.JPG?raw=true)

## 2-3. Set Models in Each Experiment

You can set identical models among the created *experiment*s using `.set_models()` method. You should pass the type (class) of the model and its hyperparameters.

## 2-4. Fit Models in Each Experiment

You can train the model sequentially using `fit_experiments()` method.
Event file for the real-time tracking of the experiment via TensorBoard is saved in {path}/{project_name}/FIT. 


![alt text](https://github.com/benchay1999/astrape/blob/main/tutorial/set_and_fit_new.JPG?raw=true)
*Astrape uses Rich ProcessBar*
## 2-5. Save Fitted Models in Each Experiment

You can save the fitted models using `.save_stacks()`, which is basically performing `.save_stack()` for the created *experiments*. Read [3-5. Saving Models](#3-5-saving-models) for details.

You can also save the fitted models using `.save_project()` method.

## 2-6. Plot Results

Astrape supports plotting results of the following:

### 2-6-1. Plot Performances With an Identical Model Type

`.plot_identical_model_type()` method plots & saves a figure showing performance of a specified model type (e.g., MLP, UNet) generated in each experiment. 

![alt text](https://github.com/benchay1999/astrape/blob/main/tutorial/plot_identical_model_type.JPG?raw=true)
*AUC among different random states*

### 2-6-2. Plot Performances With an Identical Model Structure

`.plot_identical_model_structure()` method plots & saves a figure showing performance of a specified model structure generated in each experiment. 
![alt text](https://github.com/benchay1999/astrape/blob/main/tutorial/plot_identical_model_structure.JPG?raw=true)
*AUC among different random states*

### 2-6-3. Plot Performances of All Model Structures 

`.plot_all_model_structures()` method plots & saves two figures showing performances of all model structrues created in the *project*. One is a line plot of performances among different random states and the second is a box plot of performances of all model structures. 
![alt text](https://github.com/benchay1999/astrape/blob/main/tutorial/plot_all_model_structures.JPG?raw=true)
*Upper image shows performances of all model structures and the lower image shows a boxplot of all model structures trained in the project*

# 3. Experiment

When using Astrape, we expect you to conduct all experiments inside the `experiment.Experiment` class. This class takes a number of parameters, and you can check the details in the [tutorial](https://colab.research.google.com/drive/1VZCR84K2pzKpZoFGy3kp8vOZYAYyvQjJ?usp=sharing). 

Once you declare an experiment, all random operations are governed by the same random seed you defined as a parameter for the experiment. When initialized (with a given random state) and the train/validation/test data are specified, you should now declare models for the task.

## 3-1. Specifying Models

Declare a model using `.set_model()` method. Astrape supports 1) multi-layer perceptron with all # of hidden units identical among layers (`MLP`), 2) multi-layer perceptron with # of hidden units contracting with given constant rate (`ContractingMLP`), 3) cutomizedcustomized multi-layer perceptron of which you can define numbera  of hidden units for each layer using list (`CustomMLP`), 4) VGG network (`VGG`), 5) UNet (`UNet`). The models mentioned in this paragraph are all `pytorch_lightning.LightningModules`.
 

> You can also declare sci-kit learn models and their variants(e.g., xgboost) as well using `.set_model()`. Astrape is compatible with sci-kit learn and PyTorch-lightning modules. 


## 3-2. (Optional) Specifying Trainers 

PyTorch Lightning uses `Trainer` for training, validating, and testing models. You can specify it using the `.set_trainer()` method with trainer configurations as parameters. If you don't, default values will be set for the `Trainer`. Check the [tutorial]([https://github.com/benchay1999/astrape/blob/main/tutorial/tutorial.ipynb](https://colab.research.google.com/drive/1VZCR84K2pzKpZoFGy3kp8vOZYAYyvQjJ?usp=sharing)) for details.

## 3-3. Fitting the Model

You can fit the model using `.fit()` method. When you didn't specify a `Trainer` in previous step, default settings would be used in the fitting. Else, you can specify `Trainer` implicitly by passing the trainer configurations as parameters for `.fit()`. 


> Training and valiation process of a LightningModule-Based models are visualized in real-time using TensorBoard. 

## 3-4. Stacking Fitted Models

`Experiment` class has `.stack` as an attribute. If `.stack_models` is set to `True`, fitted models will automatically be saved to `.stack`. If `.stack_models` is set to `False`, it would stop stacking fitted models to the stack. However, it would still save the model that is just fitted i.e., it will have memory of 1 fit. You can toggle `.stack_models` using `.toggle_stack_models()` method.

Plus, you can check which model in the stack has the best performance using `.best_ckpt_in_stack()`.

## 3-5. Saving Models

You can save the current model using `.save_ckpt()` method, or you can save the models in the stack using `.save_stack()` method. After `.save_stack()`, `.stack` will be flushed.

## 3-6. Checking the Best Model Thus Far

With `.best_ckpt_thus_far()` method, you can check the best model saved (in local) thus far.

## 3-7. (Stratified) K-Fold Cross-Validation

You can perform (stratified) k-fold cross-validation using `.cross_validation()` method. See details in the [tutorial](https://colab.research.google.com/drive/1VZCR84K2pzKpZoFGy3kp8vOZYAYyvQjJ?usp=sharing).

> `.cross_validation()` is compatible with sci-kit learn models and their variants(e.g., xgboost) as well. Astrape is compatible with sci-kit learn models and pytorch-lightning modules.

# Miscellaneous

## Setting Customized Pytorch-Lightning Models

## 



