Usage
=====

The :mod:`cuspy` package can be applied to a large class of models, on the
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

Command line application
------------------------

Python module
-------------

To use :mod:`cuspy` as a Python module you can simply import it and use the
functions within::

    import cuspy

You can include the previous commands in a Python script (see the scripts
in the folder :file:`tests`). To run a python script from the command line, type:

.. code:: shell

    python path_to_script

Analysis process
----------------
Preparation of the model
^^^^^^^^^^^^^^^^^^^^^^^^
Before starting the analyses, you need to prepare all the input files
and scripts required by the model.

In particular, it must be possible to execute the model using a command line
instruction of the type:

.. code:: shell

    run_model -x arg_x -y arg_y

Alternatively, if the model has binary output or several output files, you may need to
create a script to process the model output so that it conforms with the
recommended format (text file separated by spaces with the date in the first
column). For example:

.. code:: shell

    python script.py

Plus, the model must read the values of its parameters from a text file
organised in two columns separated by spaces containing parameter names
and values. For example:

::

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

Creation of PEST files
^^^^^^^^^^^^^^^^^^^^^^
The first stage in the use of the :mod:`cuspy` package is the creation of the
PEST files. You can do this manually, or you can use the function
:func:`write_pest_files`. The following is an example of the instruction
to create the PEST files for the OKP model.

.. code:: python

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
  :mod:`okplm` package.
* ``control_data``, ``svd_data`` and ``pestpp_opts`` are dictionaries used to set
  the values of variables in the control data, singular value decomposition
  and PEST++ control data sections of the pest control file.
* ``tpl_file``, ``ins_file`` and ``pst_file`` are the names of PEST files
  created by the function. The ``tpl_file`` is a template of the parameter file
  ``par_file`` used by PEST++ to modify it. The ``ins_file`` is a file indicating
  PEST++ which values in the ``output_file`` correspond to observations and predictions.
  The ``pst_file`` controls the execution of the PEST++ executables.

We describe next some of the files used by :func:`write_pest_files`. For more
information on other arguments (including some not used above), please see the
function's description in the Modules section.

The PEST control file (``pst_file``)
""""""""""""""""""""""""""""""""""""
The PEST control file contains all the information necessary to control
the execution of the PEST++ executables. It is automatically written by the function
:func:`write_pest_files` and it is divided in the following sections:

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
* **PEST++ variables** (optional) [#first]_

At the moment :mod:`cuspy` functions can be used to configure the sections in bold,
which include all mandatory sections and some optional ones. If necessary, the
other sections can be configured manually. For details on the file structure and
variables, please see PEST++ user manual.

.. [#first] Declarations of PEST++ variables (the string "++" followed by the variable
    name and value) can be located anywhere in the PEST control file,
    but they are placed at the end of the file by :func:`write_pest_files`.

The parameter data file (``par_data_file``)
"""""""""""""""""""""""""""""""""""""""""""

In the example above, ``par_data_file`` is a text file separated by spaces
containing the data of the parameter section of the PEST control file.
This file must be provided by the users, based on their previous knowledge
of the optimum parameter values and acceptable ranges of variation.

An example is shown below.

::

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
    - ``'tied'``: the parameter is tied to another parameter (not implemented in :mod:`cuspy`).

* ``parchglim``: parameter change limit. It is used by the PEST++ executables
  `pestpp-glm` and (optionally) `pestpp-ies` to limit the change a parameter
  can suffer at each iteration of the optimization process. It can take the
  values:

    - ``'relative'``: a relative limit is used, i.e., the value of the parameter
      :math:`b` must fulfill the condition :math:`|b-b_0|/|b_0| \leq r`, where
      :math:`b_0` is the parameter value at the start of the iteration and :math:`r`
      is the value of the PEST control variable ``relparmax`` (=10 by default).
    - ``'factor'``: a factor limit is used,, i.e., the value of the parameter
      :math:`b` must be within the limits :math:`|b_0/f| \leq b \leq |fb_0|`, where
      :math:`b_0` is the parameter value at the start of the iteration and :math:`f`
      is the value of the PEST control variable ``facparmax`` (=10 by default).

* ``parval1``: initial parameter value. It should be the best estimate of the parameter
  value before calibration based on expert knowledge.
* ``parlbnd`` and ``parubnd``: lower and upper bounds of the parameter value. If an uncertainty
  file is provided [#second]_, they represent the minimum and maximum values that the parameter
  can take. If an uncertainty file is not provided, they are understood to represent the
  95% confidence interval (a width of 4 standard deviations) [#third]_ of the parameter value.
* ``pargp``: parameter group name to which the parameter has been assigned.
* ``scale`` and ``offset``: multiplier (1.0 by default) and offset (0.0 by default) to
  apply to a parameter before being written to a model input file. It can be
  used to modify the parameter range of a parameter to a more convenient one
  (e.g., if the parameters takes negative values and a log transformation is envisaged).
* ``dercom``: integer indicating the line of the "model command line" section in the
  PEST control file that is used to calculate derivatives for a given parameter.
  Usually there is only one command (``dercom=1``).

.. [#second] An uncertainty file can be provided with the PEST++ control variable ``parcov``.

.. [#third] The width of the interval can be modified with the PEST++ control variable
    ``par_sigma_range``.

The observations
""""""""""""""""

The files :file:`obs.txt` and :file:`pred.txt` contain observations or measurements.
They have the same format as the model output file, but include only the available
observations. It is necessary to provide at least one of these files.

One way of looking at the data in :file:`obs.txt` is as the data used in the
calibration or history matching process. The observations in :file:`obs.txt`
receive a positive weight (1 by default) and if there is missing data
(coded as NA, NaN or nan), the corresponding rows will be ignored. The observation
weights can be modified with the argument ``obs_weights``. This is useful when
some measurements are more uncertain than others.

Instead, the observations in the :file:`pred.txt` file or predictions, may be seen
as validation data or dates for which a forecast is desired. They receive a null
weight and their value is not used in calculations.

Observations can be assigned to different groups using the arguments ``obs_groups``
and ``pred_groups``. By assigning observations to different groups, we obtain
a multiple-component objective function. For example, in the OKP model, that
estimates epilimnion and hypolimnion temperatures, measurements for each of
these two compartments may be placed in different groups.

For more complex models
this is still more useful. For example, in the GLM model, the user could have
temperature measurements taken within the lake, water temperatures at the outlet,
satellite temperatures at the surface, water level measurements, salinity measured
within the lake and salinity at the outlet. All these different types of measurement
could be assigned to different groups. Or, if the study is interested in only one aspect,
use only one of those sets of data (and only one group) to calibrate the model.

Still, Doherty & Welter (2010) recommend using multiple-component objective functions
as a way of reducing the influence of model structural error on the calibration.

The uncertainty file
""""""""""""""""""""
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

Carry the analyses
^^^^^^^^^^^^^^^^^^
This package allows you to carry several types of analysis:

* Model calibration (aka parameter estimation, history matching).
  There are four possible options:

    - Gauss-Levenberg-Marquardt (GLM) algorithm, using the
      function :func:`calibration`. It is a gradient algorithm
      for overdetermined cases.
    - GLM algorithm with Tikhonov regularisation, using the
      function :func:`calibration`. For under-determined cases.
    - Differential Evolution (DE), using the
      function :func:`calibration`. It is a global algorithm with longer
      time of computation than the previous two options.
    - Iterative ensemble smoother, using the function :func:`ies`. It is also
      a global algorithm, especially useful for nonlinear models with a large
      number of parameters, that obtains several sets of parameter values that
      can be considered to be calibrated.

* Prior (before calibration) and posterior (after calibration) uncertainty
  analysis. There are the following options:

    - Linear uncertainty analysis, using the function :func:`linear_uncertainty`.
      Appropriate for linear or quasi-linear models.
      It may be applicable to a nonlinear model if the behaviour of the
      model in the parameter space is approximately linear (:math:`R^2 > 0.7`).
      It requires a low computation time,
      once the model is calibrated. The following options are available:

        * Prior linear uncertainty analysis.
        * Schur's complement analysis for conditional uncertainty propagation.
        * Error variance analysis. It also includes identifiability estimation.

    - Nonlinear uncertainty analysis. Preferable when the model is not linear.
      However, calculation times are longer.

        * Monte Carlo simulations, using the function :func:`monte_carlo`.
          It usually requires a large number of simulations (>1000).
        * Iterative ensemble smoother, using the function :func:`ies`.
          It requires a much lower number of simulations than Monte Carlo
          methods.

* Sensitivity analysis. There are two options:

    - Local sensitivity analysis. Low computation time. It is calculated during
      calibration using the function :func:`calibration`.
    - Global sensitivity analysis (GSA). Applied using the function :func:`gsa`.
      Two implemented methods:

        * Morris's method (one parameter at a time). Low computation time.
        * Sobol's method (all parameters vary at the same time). High
          computation time.

In all cases calculations can be parallelized using the argument ``parallel=True``.

The following table shows the computational cost of several :mod:`cuspy`
functions in terms of number of model runs and run time. Run time
calculations are based on the cases presented in the :file:`tests` folder
and were made using an Ubuntu virtual machine with 4 processors of 3067
MHz. These tests consist in the application of different :mod:`cuspy`
functions to the OKP water temperature model with 8 adjustable parameters.

.. csv-table:: Computational cost of different types of analyses
    :header: **Function**, **Details**, **Parallelized**, **N. runs**, **Run time (s)**

    ":func:`calibration`", "``method='glm'``, ``noptmax=10``", Yes, 95, 101.3
    ":func:`calibration`", "``method='glm'``, ``noptmax=10``", No, 95, 192.1
    ":func:`calibration`", "``method='glm'``, ``noptmax=10``, ``reg=True``", Yes, 145, 146.6
    ":func:`calibration`", "``method='glm'``, ``noptmax=10``, ``reg=True``", No, 145, 292.6
    ":func:`calibration`", "``method='de'``, ``de_max_gen=20``", Yes, 801, 707.3
    ":func:`calibration`", "``method='de'``, ``de_max_gen=20``", No, 801, 1694.7
    ":func:`gsa`", "``method='morris'``", Yes, 36, 37.0
    ":func:`gsa`", "``method='morris'``", No, 36, 72.8
    ":func:`gsa`", "``method='sobol'``, ``gsa_sobol_samples=50``", Yes, 500, 413.4
    ":func:`gsa`", "``method='sobol'``, ``gsa_sobol_samples=50``", No, 500, 1009.1
    ":func:`monte_carlo`", "``n_samples=50`` [#fourth]_", Yes, 50, 50.9
    ":func:`monte_carlo`", "``n_samples=50`` [#fourth]_", No, 50, 103.5
    ":func:`ies`", "``noptmax=10``, ``n_reals=50``", Yes, 788, 672.2
    ":func:`ies`", "``noptmax=10``, ``n_reals=50``", No, 788, 1590.0

.. [#fourth] The number of simulations (``n_reals``) used in Monte Carlo
   experiences is usually of the order of thousands and greater. Thus calculation time
   is usually much greater than shown here.

Calibration with GLM or DE
^^^^^^^^^^^^^^^^^^^^^^^^^^
To calibrate a model you can use the function :func:`calibration`.
For example:

.. code:: python

    pst = cuspy.calibration(method='glm', reg=False,
                            pst_file0='test0.pst',
                            pst_file1='test1.pst',
                            control_data={'noptmax': 10})

The pest instance returned by the function can be used to access the results
of the calibration. To obtain the calibrated parameter values, type:

.. code:: python

    pst.write_par_summary_table()

To obtain the simulated values and residuals, type:

.. code:: python

    pst.res

And to obtain a summary of these, type:

.. code:: python

    pst.write_obs_summary_table()

You may plot the results using:

.. code:: python

    pst.plot()

In addition, a certain number of useful files is written by PEST++. Please,
see the PEST++ user guide to obtain information on these files.

Global sensitivity analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Two methods can be used to carry a global sensitivity analysis: Morris's
method and Sobol's method. You need to use the function :func:`gsa`,
by choosing the desired method ('sobol' or 'morris') and configuring
the method using the `pestpp_opts` argument. For example:

.. code:: python

    cuspy.gsa(method='sobol', pst_file0='pest.pst', pst_file1='pest3.pst',
              pestpp_folder=pestpp_folder,
              pestpp_opts={'gsa_sobol_samples': 50, 'gsa_sobol_par_dist': 'unif'})


Linear uncertainty analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the function is calibrated, you can make a linear uncertainty analysis
using the function :func:`linear_uncertainty`. For example:

.. code:: python

    la = cuspy.linear_uncertainty(analysis='prior', pst_file0='test6.pst',
                                  pst_file1='test6b.pst',
                                  pestpp_folder=pestpp_folder)

Prior uncertainty
"""""""""""""""""

The :class:`LinearAnalysis` object returned by the function can be used
to access the results of the uncertainty analysis. To obtain the prior uncertainty
of predictions, type:

.. code:: python

    la.prior_forecast

Posterior uncertainty
"""""""""""""""""""""
To carry a Schur's complement analysis, you need to set ``analysis='schur'``.
For example:

.. code:: python

    la_sc = cuspy.linear_uncertainty(analysis='schur', pst_file0='test6.pst',
                                     pst_file1='test6b.pst',
                                     pestpp_folder=pestpp_folder)

With Schur's complement analysis you can obtain the
posterior uncertainty typing:

.. code:: python

    la_sc.posterior_forecast

To obtain prior and posterior uncertainties for the predictions
of interest and the reduction in uncertainty due to calibration ('schur'), type:

.. code:: python

    forecast_sum = la_sc.get_forecast_summary()

Similarly, you can obtain information on the reduction of parameter uncertainty
through calibration by typing:

.. code:: python

    parameter_sum = la_sc.get_parameter_summary()

Data worth
""""""""""

It is possible to analyse data worth with the :class:`Schur` object
returned by the function :func:`linear_uncertainty`.
The following instructions return the variance of the predictions after
adding a new observation or group of observations:

.. code:: python

    la_sc.get_added_obs_importance()
    la_sc.get_added_obs_group_importance()

A similar analysis can be made by removing observations or groups of observations
with the methods :meth:`get_removed_obs_importance` and
:meth:`get_removed_obs_group_importance`.

To obtain the contribution of each parameter to prediction uncertainty,
type:

.. code:: python

    la_sc.get_par_contribution()

Predictive error
""""""""""""""""
To analyse predictive error with an error variance analysis you need to
set ``analysis='err_var'``. For example:

.. code:: python

    la_ev = cuspy.linear_uncertainty(analysis='err_var', pst_file0='test6.pst',
                                     pst_file1='test6b.pst',
                                     pestpp_folder=pestpp_folder)


The :class:`ErrVar` object returned by the function :func:`linear_uncertainty`
allows to access the results of the error variance analysis:

.. code:: python

    la_ev.get_errvar_dataframe()

Identifiability
"""""""""""""""
With the :class:`ErrVar` object, it is also possible to access the results
of the identifiability analysis with:

.. code:: python

    la_ev.get_identifiability_dataframe()

Monte Carlo simulations
^^^^^^^^^^^^^^^^^^^^^^^
To carry Monte Carlo simulations with the :mod:`cuspy` package you can use
the function :func:`monte_carlo`. For example:

.. code:: python

    cuspy.monte_carlo(pst_file0='test1.pst', pst_file1='test4.pst',
                      dist_type='post', distribution='uniform',
                      n_samples=5000, pestpp_folder=pestpp_folder,
                      csv_in='sweep_in.csv', parallel=parallel)

The sets of parameter values drawn from the specified distribution are saved
in the `csv_in` file (:file:`sweep_in.csv` by default). The simulation
results are also saved to a csv file, named :file:`sweep_out.csv` by default.
The name of the output csv file can be modified using the `pestpp_opts` argument:

.. code:: python

    cuspy.monte_carlo(pst_file0='test1.pst', pst_file1='test4.pst',
                      dist_type='post', distribution='uniform',
                      n_samples=5000, pestpp_folder=pestpp_folder,
                      csv_in='sweep_in.csv', parallel=parallel,
                      pestpp_opts={'sweep_output_csv_file': 'sweep_out.csv'})

Monte Carlo simulations can have several uses,
including calibration, global sensitivity analyses and uncertainty
analyses, depending on how the simulation results are analysed. No
particular type of analysis is implemented in this package, but they
can be easily implemented based on the treatment of the input and output
csv files (`csv_in` and `sweep_output_csv_file`).

Iterative Ensemble Smoothing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To apply the IES method, you need to use the function :func:`ies`.
For example:

.. code:: python

    cuspy.ies(pst_file0='test0.pst', pst_file1='test5.pst',
              pestpp_folder=pestpp_folder, n_reals=50,
              control_data={'noptmax': 10})

The implementation of the IES method uses the GLM algorithm (called with
`pestpp-glm`), which can be configured using the `pst_file0` and
`control_data` arguments. The IES method can be configured with the
`pestpp_opts` argument.

The output of the :func:`ies` function can be found in a series of csv
files. The optimized parameter value sets can be found in the file
:file:`case.N.par.csv`, where "case" is the name of the pest file
`pst_file1` and "N" is the number of the latest iteration.
The simulation results for each parameter set can be found in the file
:file:`case.N.obs.csv`. The objective function results during all iterations
can be found in the files :file:`case.phi.actual.csv` (objective function
calculated from differences between forecasts and observations),
:file:`case.phi.meas.csv` (objective function calculated from differences
between forecasts and noisy observations), :file:`case.phi.group.csv`
(objective function calculated by parameter and observation groups) and
:file:`case.phi.regul.csv` (regularization objective functions).

References
----------

* Doherty, J.; Welter, D. (2010) A short exploration of structural noise.
  *Water Resources Research*, 46, W05525.
