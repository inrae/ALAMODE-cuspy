Example data to test the package :mod:`cuspy`
=============================================

You can test the application with example data provided in the folder
:file:`example_data` and the OKP model implemented in the :mod:`okplm` package.
Several scripts that use these data and model are also available in the folder
:file:`tests`.

The data
--------

The lake data in the :file:`lake.txt` file corresponds to the Lake Allos
(lake code = ALL04).

The meteorological data (:file:`meteo.txt`) is synthetic data
based on meteorological data. Air temperature has been created using a seasonal
component and an ARMA model, while solar radiation data corresponds to the
seasonal component only.

The observations in the files :file:`obs.txt` and :file:`pred.txt` are
fictitious and their only aim is to verify the package is working correctly
and to help learn its usage.

The folder also contains three files containing observation names
(:file:`obs_names.txt`), observation group names (:file:`obs_groups.txt`)
and observation weights (:file:`obs_weights.txt`).

The scripts
-----------
The folder :file:`tests` contains several scripts that can be used to test
the package functionalities. Each script illustrates how to make different
types of analysis.

The included scripts are:

* :file:`test_0_input.py`: it illustrates input file management.
* :file:`test_1_overdet.py`: it provides examples of calibration in the
  overdetermined case, with GLM or DE algorithms.
* :file:`test_2_calib_reg.py`: it provides an example of calibration in the
  under-determined case, using Tikhonov regularisation.
* :file:`test_3_sensitivity.py`: it exemplifies the realisation of a
  global sensitivity analysis.
* :file:`test_4_monte_carlo.py`: it shows how to carry Monte Carlo
  simulations.
* :file:`test_5_ies.py`: it shows an application of Iterative Ensemble
  Smoothing.
* :file:`test_6_uncertainty.py`: it shows an example of calibration and
  uncertainty analysis.
