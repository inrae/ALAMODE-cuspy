Presentation
============
What is the :mod:`cuspy` package?
---------------------------------
The package :mod:`cuspy` (Calibration, Uncertainty and Sensitivity analysis in PYthon)
is a package in Python 3 that provides tools for parameter estimation,
and sensitivity and uncertainty analyses of models.

The package is based on the use of the Python package :mod:`pyemu`
(White et al. 2016) and the PEST++ suite of software tools
(White et al. 2019). PEST and PEST++ (Doherty et al. 2018) are software
suites designed for and used mainly by the hydrological community. They
implement several linear and nonlinear uncertainty analysis, calibration
methods and global sensitivity analyses. The package :mod:`pyemu` offers a
Python interface to use and configure PEST++ tools and to access and
process their results.

However, the package :mod:`cuspy` does not offer all the functionalities
of PEST++ and :mod:`pyemu` (for example, tied parameters are not supported).
In fact, the package :mod:`cuspy` has been designed with the objective of facilitating
the application of :mod:`pyemu` and PEST++ functionalities to the water
temperature models and hydrological models implemented with the packages
:mod:`okplm`, :mod:`glmtools` and :mod:`tributary`. Still, the design of the
package is sufficiently general to be quite model-independent. The main
requirements are that the model can be run through the command line and
that it communicates with the user through text files.

Authors
-------
* Jordi Prats-Rodríguez (jprats@segula.es)
* Pierre-Alain Danis (pierre-alain.danis@ofb.gouv.fr)

References
----------
* Doherty, J.; White, J.; Welter, D. (2018) *PEST & PEST++. An
  Overview.* Watermark Numerical Computing. 48 p.
* White, J.T.; Fienen, M.N.; Doherty, J.E. (2016) A python framework for
  environmental model uncertainty analysis.
  *Environmental Modelling & Software*, 85, 217-228,
  doi: `10.1016/j.envsoft.2016.08.017
  <https://dx.doi.org/10.1016/j.envsoft.2016.08.017>`_.
* White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version 4.2.16.*
  PEST++ Development Team.
