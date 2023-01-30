# cuspy : Calibration, Uncertainty and Sensitivity analysis in PYthon
Copyright 2020-2023 Segula Technologies - Office Français de la Biodiversité.

<p align="center">
<img title="banner ALAMODE" src="images/ALAMOD_withlogos.png">
</p>

[![DOI](https://zenodo.org/badge/594141785.svg)](https://zenodo.org/badge/latestdoi/594141785)

## Content

1. [What is the cuspy package?](#purpose)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Dependencies](#dependencies)
5. [Usage](#Usage)
6. [Examples for okp](#Examples)
7. [References](#references)

<a name="purpose"></a>

## What is the cuspy package ?

`cuspy` is a package ALAMODE software in python 3 that provides
tools for parameter estimation, and sensitivity and uncertainty analyses of models.

The package is based on the use of the Python package pyemu (White et al. 2016) and the PEST++ suite of software
tools (White et al. 2019). PEST and PEST++ (Doherty et al. 2018) are software suites designed for and used mainly
by the hydrological community. They implement several linear and nonlinear uncertainty analysis, calibration methods
and global sensitivity analyses. The package pyemu offers a Python interface to use and configure PEST++ tools and
to access and process their results.

However, the package cuspy does not offer all the functionalities of PEST++ and pyemu (for example, tied parameters
are not supported). In fact, the package cuspy has been designed with the objective of facilitating the application of
pyemu and PEST++ functionalities to the water temperature models and hydrological models implemented with the
packages okplm, glmtools and tributary. Still, the design of the package is sufficiently general to be quite model-
independent. The main requirements are that the model can be run through the command line and that it communicates
with the user through text files.

__Authors__ :

* Jordi Prats-Rodríguez (jprats@segula.es)
* Pierre-Alain Danis (pierre-alain.danis@ofb.gouv.fr)

<a name="requirements"></a>

## Requirements

You need Python 3.5 or later to run the `cuspy` package. You can have
multiple Python versions (2.x and 3.x) installed on the same system
without problems.


<a name="installation"></a>

## Installation
### Cloning the repository
First you have to clone the `cuspy` package with git:
```git
git clone https://github.com/inrae/ALAMODE-cuspy
```
This command creates the okplm repertory.


### Installing `cuspy`
Using septuptools:
```bash
cd pathtorepertorycuspy
python setup.py install
```
Using pip :
```bash
cd pathtorepertorycuspy
pip install -U .
```


<a name="dependencies"></a>

## Dependencies

The application `cuspy` depends on the following Python packages:

* numpy
* pandas
* pyemu==1.0


<a name="Usage"></a>

## Usage

The `cuspy` package can be applied to a large class of models, on the
condition that:

* the model can be run using the command line (e.g., through an executable
  that is available in the path or a call to a script).
* the communication between the model and the user (output data, parameter
  values) is made by means of text files (or the script calling the model
  reads data in binary form and creates output in text form).

In addition, the package has been specially designed to work with dynamic
models the output of which is in several columns, the first of which is date.
Working with models with other type of output is possible, but it requires more
implication of the user in the preparation of the PEST instruction files.

### Python module

To use `cuspy` as a Python module you can simply import it and use the
functions within::

```bash
import cuspy
```

You can include the previous commands in a Python script (see the scripts
in the folder `tests`). To run a python script from the command line, type:

```bash
python path_to_script
```

### Analysis process
#### Preparation of the model

Before starting the analyses, you need to prepare all the input files
and scripts required by the model.

In particular, it must be possible to execute the model using a command line
instruction of the type:

```bash
run_model -x arg_x -y arg_y
```

Alternatively, if the model has binary output or several output files, you may need to
create a script to process the model output so that it conforms with the
recommended format (text file separated by spaces with the date in the first
column). For example:

```bash
python script.py
```

Plus, the model must read the values of its parameters from a text file
organised in two columns separated by spaces containing parameter names
and values. For example:

    A 6.2
    B 1.007
    C -0.007
    D 0.51
    E 0.24
    ALPHA 0.07
    BETA 0.13
    mat -0.4
    at_factor 1.0
    sw_factor 1.0

#### Creation of PEST files

The first stage in the use of the `cuspy` package is the creation of the
PEST files. You can do this manually, or you can use the function
`write_pest_files()`. The following is an example of the instruction
to create the PEST files for the OKP model.

```python
cuspy.write_pest_files(start_date=start_date, end_date=end_date,
                       par_file='par.txt', output_file='output.txt',
                       par_data_file='par_data.csv',
                       obs_file='obs.txt', pred_file='pred.txt',
                       model_command='run_okp',
                       control_data={'noptmax': 0, 'numlam': 10},
                       svd_data={'maxsing': len(par_names)},
                       pestpp_opts={'parcov': uncertainty_file},
                       tpl_file='par.tpl', ins_file='res_file.ins',
                       pst_file='test0.pst')
```

In the previous example, we can notice the following facts:

* ``start_date`` and ``end_date`` correspond to the initial and final dates
  of the simulation.
* ``par_file`` and ``output_file`` are the names of the model's parameter and
  output files.
* ``par_data_file``, ``obs_file`` and ``pred_file`` are space-separated text
  files used to pass parameter and observation data to the function. These must
  be prepared by the user.
* ``model_command`` is the command line instruction used to run the model. In
  this case, the model OKP is run using the instruction ``run_okp`` of the
  `okplm` package.
* ``control_data``, ``svd_data`` and ``pestpp_opts`` are dictionaries used to set
  the values of variables in the control data, singular value decomposition
  and PEST++ control data sections of the pest control file.
* ``tpl_file``, ``ins_file`` and ``pst_file`` are the names of PEST files
  created by the function. The ``tpl_file`` is a template of the parameter file
  ``par_file`` used by PEST++ to modify it. The ``ins_file`` is a file indicating
  PEST++ which values in the ``output_file`` correspond to observations and predictions.
  The ``pst_file`` controls the execution of the PEST++ executables.

We describe next some of the files used by `write_pest_files()`. For more
information on other arguments (including some not used above), please see the
user manual.

#### The PEST control file (``pst_file``)

The PEST control file contains all the information necessary to control
the execution of the PEST++ executables. It is automatically written by the function
`write_pest_files()` and it is divided in the following sections:

* **control data** (mandatory)
* automatic user intervention (optional)
* **singular value decomposition** (optional)
* lsqr (optional)
* sensitivity reuse (optional)
* svd assist (optional)
* **parameter groups** (mandatory)
* **parameter data** (mandatory)
* **observation groups** (mandatory)
* **observation data** (mandatory)
* derivatives command line (optional)
* **model command line** (mandatory)
* **model input** (mandatory)
* **model output** (mandatory)
* prior information (optional)
* predictive analysis (optional)
* **regularization** (optional)
* pareto (optional)
* **PEST++ variables** (optional)

At the moment `cuspy` functions can be used to configure the sections in bold,
which include all mandatory sections and some optional ones. If necessary, the
other sections can be configured manually. For details on the file structure and
variables, please see PEST++ user manual.

#### The parameter data file (``par_data_file``)

In the example above, ``par_data_file`` is a text file separated by spaces
containing the data of the parameter section of the PEST control file.
This file must be provided by the users, based on their previous knowledge
of the optimum parameter values and acceptable ranges of variation.

An example is shown below.

    parnme partrans parchglim parval1 parlbnd parubnd pargp scale offset dercom
    a none relative 6.2 4.7 7.7 a 1.0 0.0 1
    b none relative 1.007 0.847 1.167 b 1.0 0.0 1
    c none relative -0.0069 -0.015 0.001 c 1.0 0.0 1
    d none relative 0.51 0.0 1.0 d 1.0 0.0 1
    e none relative 0.24 0.0 1.0 e 1.0 0.0 1
    alpha none relative 0.07 0.0 0.23 alpha 1.0 0.0 1
    beta none relative 0.13 0.0 1.0 beta 1.0 0.0 1
    mat none relative 2.4 1.4 3.4 mat 1.0 0.0 1
    at_factor fixed relative 1.0 0.9 1.1 at_factor 1.0 0.0 1
    sw_factor fixed relative 1.0 0.9 1.1 sw_factor 1.0 0.0 1

The first line of the file contains the column names, described below:

* ``parnme``: parameter name (up to 200 characters, case insensitive).
* ``partrans``: parameter transformation. It takes one of four possible values:

    - ``'none'``: no transformation applied to the parameter.
    - ``'log'``: the parameter is log-transformed.
    - ``'fixed'``: constant or non-adjustable parameter.
    - ``'tied'``: the parameter is tied to another parameter (not implemented in `cuspy`).

* ``parchglim``: parameter change limit. It is used by the PEST++ executables
  `pestpp-glm` and (optionally) `pestpp-ies` to limit the change a parameter
  can suffer at each iteration of the optimization process. It can take the
  values:

    - ``'relative'``: a relative limit is used, i.e., the value of the parameter
      $`b`$ must fulfill the condition $`|b-b_0|/|b_0| \leq r`$, where
      $`b_0`$ is the parameter value at the start of the iteration and $`r`$
      is the value of the PEST control variable ``relparmax`` (=10 by default).
    - ``'factor'``: a factor limit is used,, i.e., the value of the parameter
      $`b`$ must be within the limits $`|b_0/f| \leq b \leq |fb_0|`$, where
      $`b_0`$ is the parameter value at the start of the iteration and $`f`$
      is the value of the PEST control variable ``facparmax`` (=10 by default).

* ``parval1``: initial parameter value. It should be the best estimate of the parameter
  value before calibration based on expert knowledge.
* ``parlbnd`` and ``parubnd``: lower and upper bounds of the parameter value. 
* ``pargp``: parameter group name to which the parameter has been assigned.
* ``scale`` and ``offset``: multiplier (1.0 by default) and offset (0.0 by default) to
  apply to a parameter before being written to a model input file. It can be
  used to modify the parameter range of a parameter to a more convenient one
  (e.g., if the parameters takes negative values and a log transformation is envisaged).
* ``dercom``: integer indicating the line of the "model command line" section in the
  PEST control file that is used to calculate derivatives for a given parameter.
  Usually there is only one command (``dercom=1``).

#### The observations

The files `obs.txt` and `pred.txt` contain observations or measurements.
They have the same format as the model output file, but include only the available
observations. It is necessary to provide at least one of these files.

One way of looking at the data in `obs.txt` is as the data used in the
calibration or history matching process. The observations in `obs.txt`
receive a positive weight (1 by default) and if there is missing data
(coded as `NA`, `NaN` or `nan`), the corresponding rows will be ignored. The observation
weights can be modified with the argument ``obs_weights``. This is useful when
some measurements are more uncertain than others.

Instead, the observations in the `pred.txt` file or predictions, may be seen
as validation data or dates for which a forecast is desired. They receive a null
weight and their value is not used in calculations.

Observations can be assigned to different groups using the arguments ``obs_groups``
and ``pred_groups``. By assigning observations to different groups, we obtain
a multiple-component objective function. For example, in the OKP model, that
estimates epilimnion and hypolimnion temperatures, measurements for each of
these two compartments may be placed in different groups.

#### The uncertainty file

Information on prior parameter uncertainty can be provided to PEST++ through an uncertainty
file using the PEST++ control variable ``parcov``. This file can take several forms:

* A parameter uncertainty file (.unc). It contains standard deviations for individual
  parameters that have no statistical correlation with other parameters and/or
  indicates the name of covariance matrix files for other parameters.
* A single prior covariance matrix file (.cov). It contains a covariance matrix
  of all the model's parameters. The file is written according to the PEST matrix
  file specifications.
* A binary covariance matrix file (.jco or .jcb). It is a file used by PEST++
  to write a Jacobian matrix.

For more information on the specification of these types of file see the PEST++ user
guide.

If an uncertainty file is not provided, parameter uncertainty is estimated from
the parameter bounds by assuming the interval covers 4 standard deviations.

#### Carrying the analyses

This package allows you to carry several types of analysis:

* Model calibration (aka parameter estimation, history matching).
  There are four possible options:

    - Gauss-Levenberg-Marquardt (GLM) algorithm, using the
      function `calibration()`. It is a gradient algorithm
      for overdetermined cases.
    - GLM algorithm with Tikhonov regularisation, using the
      function `calibration()`. For under-determined cases.
    - Differential Evolution (DE), using the
      function `calibration()`. It is a global algorithm with longer
      time of computation than the previous two options.
    - Iterative ensemble smoother, using the function `ies()`. It is also
      a global algorithm, especially useful for nonlinear models with a large
      number of parameters, that obtains several sets of parameter values that
      can be considered to be calibrated.

* Prior (before calibration) and posterior (after calibration) uncertainty
  analysis. There are the following options:

    - Linear uncertainty analysis, using the function `linear_uncertainty()`.
      Appropriate for linear or quasi-linear models.
      It may be applicable to a nonlinear model if the behaviour of the
      model in the parameter space is approximately linear ($`R^2 > 0.7`$).
      It requires a low computation time,
      once the model is calibrated. The following options are available:

        * Prior linear uncertainty analysis.
        * Schur's complement analysis for conditional uncertainty propagation.
        * Error variance analysis. It also includes identifiability estimation.

    - Nonlinear uncertainty analysis. Preferable when the model is not linear.
      However, calculation times are longer.

        * Monte Carlo simulations, using the function `monte_carlo()`.
          It usually requires a large number of simulations (>1000).
        * Iterative ensemble smoother, using the function `ies()`.
          It requires a much lower number of simulations than Monte Carlo
          methods.

* Sensitivity analysis. There are two options:

    - Local sensitivity analysis. Low computation time. It is calculated during
      calibration using the function `calibration()`.
    - Global sensitivity analysis (GSA). Applied using the function `gsa()`.
      Two implemented methods:

        * Morris's method (one parameter at a time). Low computation time.
        * Sobol's method (all parameters vary at the same time). High
          computation time.

In all cases calculations can be parallelized using the argument ``parallel=True``.


<a name="Examples"></a>

## Examples for cuspy

You can test the application with example data provided in the folder
`example_data` and the OKP model implemented in the `okplm` package.
Several scripts that use these data and model are also available in the folder
`tests`.

### The data

The lake data in the `lake.txt` file corresponds to the Lake Allos
(lake code = ALL04).

The meteorological data (`meteo.txt`) is synthetic data
based on meteorological data. Air temperature has been created using a seasonal
component and an ARMA model, while solar radiation data corresponds to the
seasonal component only.

The observations in the files `obs.txt` and `pred.txt` are
fictitious and their only aim is to verify the package is working correctly
and to help learn its usage.

The folder also contains three files containing observation names
(`obs_names.txt`), observation group names (`obs_groups.txt`)
and observation weights (`obs_weights.txt`).

### The scripts

The folder `tests` contains several scripts that can be used to test
the package functionalities. Each script illustrates how to make different
types of analysis.

The included scripts are:

* `test_0_input.py`: it illustrates input file management.
* `test_1_overdet.py`: it provides examples of calibration in the
  overdetermined case, with GLM or DE algorithms.
* `test_2_calib_reg.py`: it provides an example of calibration in the
  under-determined case, using Tikhonov regularisation.
* `test_3_sensitivity.py`: it exemplifies the realisation of a
  global sensitivity analysis.
* `test_4_monte_carlo.py`: it shows how to carry Monte Carlo
  simulations.
* `test_5_ies.py`: it shows an application of Iterative Ensemble
  Smoothing.
* `test_6_uncertainty.py`: it shows an example of calibration and
  uncertainty analysis.

<a name="references"></a>

# References

* Doherty, J.; White, J.; Welter, D. (2018) *PEST & PEST++. An
  Overview.* Watermark Numerical Computing. 48 p.
* White, J.T.; Fienen, M.N.; Doherty, J.E. (2016) A python framework for
  environmental model uncertainty analysis.
  *Environmental Modelling & Software*, 85, 217-228, doi: 
  [10.1016/j.envsoft.2016.08.017](https://dx.doi.org/10.1016/j.envsoft.2016.08.017).
* White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version 4.2.16.*
  PEST++ Development Team.
