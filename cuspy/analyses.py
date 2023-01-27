"""Functions to make analyses based on PEST++.

The functions in this module carry the different type of analyses
implemented in the package.

This module contains the following functions:

    * :func:`calibration`: calibrate model.
    * :func:`gsa`: Global Sensitivity Analysis.
    * :func:`ies`: Iterative Ensemble Smoother.
    * :func:`linear_uncertainty`: predictive uncertainty.
    * :func:`monte_carlo`: Monte Carlo simulations.

"""
# Copyright 2020-2023 Segula Technologies - Office Français de la Biodiversité.
#
# This file is part of the Python package "cuspy".
#
# The package "cuspy" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The package "cuspy" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "cuspy".  If not, see <https://www.gnu.org/licenses/>.
import os.path

import pyemu

from cuspy import launch_pestpp, process_sweep_out


def calibration(method='glm', reg=False, pst_file0='pest.pst',
                pst_file1='pest.pst', pestpp_folder='..', control_data=None,
                svd_data=None, reg_data=None, pestpp_opts=None,
                parallel=False):
    """Calibrate model (GLM or DE methods).

    Args:
        method: method used to calibrate the model. It is 'glm' for the
            Gauss-Levenberg-Marquardt algorithm, 'de' for differential
            evolution.
        reg: use Tikhonov regularisation.
        pst_file0: path of original pest file.
        pst_file1: path of modified pest file.
        pestpp_folder: folder containing the PEST++ executables.
        control_data: a dictionary defining options in the control data
            section of the pest file.
        svd_data: a dictionary used to pass options to the svd section
            of the pest file.
        reg_data: a dictionary used to pass options to the
            regularization section of the pest file.
        pestpp_opts: a dictionary used to pass options to configure the
            DE method.
        parallel: parallelize model runs.

    Returns:
        A pest instance where the parameter values correspond to the
        calibrated values. A pest file (`pst_file1`) and associated files
        containing the results of the calibration process are also
        created.

    Note:
        This function calls the PEST++ executable `pestpp-glm`.

    References:
        * Doherty, J. (2010) *Methodologies and Software for PEST-Based
          Model Predictive Uncertainty Analysis.* Watermark Numerical
          Computing. 157 p.
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    # Load pst file
    pst0 = pyemu.Pst(pst_file0)
    nobs = pst0.nobs
    npar = pst0.npar

    # Set calibration method
    if method == 'glm':
        # Make sure 'DE' is not used
        if 'global_opt' in pst0.pestpp_options:
            pst0.pestpp_options.pop('global_opt')
    elif method == 'de':
        pst0.pestpp_options['global_opt'] = 'de'
        if pestpp_opts is None:
            pestpp_opts = {}
        for k in pestpp_opts:
            pst0.pestpp_options[k] = pestpp_opts[k]
    else:
        raise ValueError('Method not recognised. Choose "glm" or "de".')

    # Set regularisation configuration
    if nobs < npar:
        if not reg:
            msg = 'nobs < npar, regularisation activated ' +\
                '(value of variable reg switched to True).'
            raise Warning(msg)
        reg = True

    if reg:
        pyemu.helpers.zero_order_tikhonov(pst0)
        if reg_data is None:
            reg_data = {}
        for k in reg_data:
            pst0.reg_data.__setattr__(k, reg_data[k])
    else:
        pst0.control_data.pestmode = 'estimation'

    # Configure control data
    if control_data is None:
        control_data = {}
    for k in control_data:
        pst0.control_data.__setattr__(k, control_data[k])

    # Configure SVD data
    if svd_data is None:
        svd_data = {}
    for k in svd_data:
        pst0.svd_data.__setattr__(k, svd_data[k])

    # Write modified pest file
    pst0.write(pst_file1)

    # Calibrate model
    launch_pestpp(pst_file=pst_file1, pestpp_folder=pestpp_folder,
                  pestpp_cmd='pestpp-glm', parallel=parallel)

    # Update pst
    pst1 = pyemu.Pst(pst_file1)
    pst1.parrep()

    return pst1


def ies(pst_file0, pst_file1, pestpp_folder, n_reals=50, parcov=None,
        control_data=None, svd_data=None, reg_data=None, pestpp_opts=None,
        parallel=True):
    """Iterative Ensemble Smoother.

    Args:
        pst_file0: path of original pest file.
        pst_file1: path of modified pest file.
        pestpp_folder: folder containing the PEST++ executables.
        n_reals: number of realizations.
        parcov: name of prior parameter covariance file. If None,
            parameter covariance is estimated from parameter bounds.
        control_data: a dictionary defining options in the control data
            section of the pest file.
        svd_data: a dictionary used to pass options to the svd section
            of the pest file.
        reg_data: a dictionary used to pass options to the
            regularization section of the pest file.
        pestpp_opts: a dictionary containing additional options to pass
            to `pestpp-ies`.
        parallel: parallelize calculations.

    Returns:
        A modified pest control file and the associated output files.

    Note:
        This function calls the PEST++ executable `pestpp-ies`.

    References:
        * White, J. T. (2018) A model-independent iterative ensemble
          smoother for efficient history-matching and uncertainty
          quantification in very high dimensions. *Environmental
          Modelling & Software*, 109, 191-201.
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    # Load pst instance
    pst0 = pyemu.Pst(pst_file0)

    # Configure control data
    if control_data is None:
        control_data = {}
    for k in control_data:
        pst0.control_data.__setattr__(k, control_data[k])

    # Configure SVD data
    if svd_data is None:
        svd_data = {}
    for k in svd_data:
        pst0.svd_data.__setattr__(k, svd_data[k])

    # Configure regularization data
    if reg_data is None:
        reg_data = {}
    for k in reg_data:
        pst0.reg_data.__setattr__(k, reg_data[k])

    # Set IES options
    if pestpp_opts is None:
        pestpp_opts = {}
    pst0.pestpp_options.update(pestpp_opts)
    pst0.pestpp_options['ies_num_reals'] = n_reals
    if parcov is not None:
        pst0.pestpp_options['parcov'] = parcov

    # Write modified pest control file
    pst0.write(pst_file1)

    # Launch simulations
    launch_pestpp(pst_file=pst_file1, pestpp_folder=pestpp_folder,
                  pestpp_cmd='pestpp-ies', parallel=parallel)
    return


def monte_carlo(pst_file0='pest.pst', pst_file1='pest.pst', dist_type='post',
                distribution='gaussian', n_samples=100, how_dict=None,
                csv_in='sweep_in.csv', pestpp_folder='..', add_base=False,
                control_data=None, svd_data=None, reg_data=None,
                pestpp_opts=None, parallel=True, process_swp_out=False):
    """Monte Carlo simulations.

    Args:
        pst_file0: path of original pest file.
        pst_file1: path of modified pest file.
        dist_type: type of distribution; 'prior' for prior distribution
            or 'post' for posterior distribution.
        distribution: 'uniform', 'triangular', 'gaussian', 'mixed'.
            Ignored if ``type = post`` (gaussian distribution used).
        n_samples: number of samples to draw.
        how_dict: dictionary of parameter names (keys) and distributions
            (values). Only used if ``distribution = mixed``.
        csv_in: name of the file to save the parameter samples.
        pestpp_folder: folder containing the PEST++ executables.
        add_base: add the `pst_file0` parameter values as a realization.
        control_data: a dictionary defining options in the control data
            section of the pest file.
        svd_data: a dictionary used to pass options to the svd section
            of the pest file.
        reg_data: a dictionary used to pass options to the
            regularization section of the pest file.
        pestpp_opts: a dictionary used to pass options to configure the
            `pestpp-swp` options.
        parallel: parallelize calculations.
        process_swp_out: option to process the sweep_out.csv results
            file. Observation group names should correspond to the names
            of the variables to which the observations belong.

    Returns:
        A modified pest control file and the associated output files.

    Note:
        This function calls the PEST++ executable `pestpp-swp`.

    References:
        * White, J.T.; Fienen, M.N.; Doherty, J.E. (2016) A python
          framework for environmental model uncertainty analysis.
          *Environmental Modelling & Software*, 85, 217-228.
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    # Load pest instance
    pst1 = pyemu.Pst(pst_file0)

    # Configure control data
    if control_data is None:
        control_data = {}
    for k in control_data:
        pst1.control_data.__setattr__(k, control_data[k])

    # Configure SVD data
    if svd_data is None:
        svd_data = {}
    for k in svd_data:
        pst1.svd_data.__setattr__(k, svd_data[k])

    # Configure regularization data
    if reg_data is None:
        reg_data = {}
    for k in reg_data:
        pst1.reg_data.__setattr__(k, reg_data[k])

    # Configure pestpp options
    if pestpp_opts is None:
        pestpp_opts = {}
    pst1.pestpp_options.update(pestpp_opts)

    # Set sweep_parameter_csv_file
    pst1.pestpp_options['sweep_parameter_csv_file'] = csv_in

    # Write modified pst file
    pst1.write(pst_file1)

    # Load parameter covariance
    if dist_type == 'prior':
        parcov = pyemu.Cov.from_parameter_data(pst1)
    elif dist_type == 'post':
        fname = pst_file0.rstrip('.pst') + '.post.cov'
        parcov = pyemu.Matrix.from_ascii(fname)
        distribution = 'gaussian'
    else:
        raise KeyError

    # Draw samples
    if distribution == 'gaussian':
        pe = pyemu.ParameterEnsemble.\
            from_gaussian_draw(pst=pst1, cov=parcov, num_reals=n_samples,
                               by_groups=False)
        pe.enforce(how='reset')
    elif distribution == 'uniform':
        pe = pyemu.ParameterEnsemble.from_uniform_draw(pst=pst1,
                                                       num_reals=n_samples)
    elif distribution == 'triangular':
        pe = pyemu.ParameterEnsemble.from_triangular_draw(pst=pst1,
                                                          num_reals=n_samples)
    elif distribution == 'mixed':
        pe = pyemu.ParameterEnsemble.\
            from_mixed_draws(pst=pst1, how_dict=how_dict, num_reals=n_samples,
                             cov=parcov, enforce_bounds=True)
    else:
        raise KeyError
    if add_base:
        pe.add_base()

    # Save draw to csv
    pe.to_csv(csv_in)

    # Run simulations
    launch_pestpp(pst_file=pst_file1, pestpp_folder=pestpp_folder,
                  pestpp_cmd='pestpp-swp', parallel=parallel)

    if process_swp_out:
        # Process results
        try:
            csv_out = pst1.pestpp_options['sweep_output_csv_file']
            folder_out = os.path.dirname(csv_out)
        except KeyError:
            folder_out = os.path.dirname(csv_in)
            csv_out = os.path.join(folder_out, 'sweep_out.csv')
        process_sweep_out(fname_in=csv_out, var_names=pst1.obs_groups,
                          folder_out=folder_out)

    return


def gsa(method='morris', pst_file0='pest.pst', pst_file1='pest.pst',
        control_data=None, svd_data=None, reg_data=None, pestpp_opts=None,
        pestpp_folder='..', parallel=True):
    """Carry global sensitivity analysis (Morris or Sobol methods).

    Args:
        method: 'morris' for Morris's method (one parameter at a time)
            or 'sobol' for Sobol's method.
        pst_file0: path of original pest file.
        pst_file1: path of modified pest file.
        control_data: a dictionary defining options in the control data
            section of the pest file.
        svd_data: a dictionary used to pass options to the svd section
            of the pest file.
        reg_data: a dictionary used to pass options to the
            regularization section of the pest file.
        pestpp_opts: a dictionary used to pass options to configure the
            GSA method.
        pestpp_folder: folder containing the PEST++ executables.
        parallel: parallelize model runs.

    Returns:
        A modified pst file and associated files containing results.

    Note:
        This function calls the PEST++ executable `pestpp-sen`.

    References:
        * Saltelli, A.; Ratto, M.; Andres, T.; Campolongo, F.; Cariboni,
          J.; Gatelli, D.; Saisana, M.; Tarantola, S. (2008) *Global
          Sensitivity Analysis. The Primer.* John Wiley & Sons, Ltd.
          292 p.
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    # load pest file
    pst0 = pyemu.Pst(pst_file0)

    # Configure control data
    if control_data is None:
        control_data = {}
    for k in control_data:
        pst0.control_data.__setattr__(k, control_data[k])

    # Configure SVD data
    if svd_data is None:
        svd_data = {}
    for k in svd_data:
        pst0.svd_data.__setattr__(k, svd_data[k])

    # Configure regularization data
    if reg_data is None:
        reg_data = {}
    for k in reg_data:
        pst0.reg_data.__setattr__(k, reg_data[k])

    # Configure pst file for sensitivity analysis
    pst0.pestpp_options['gsa_method'] = method
    if pestpp_opts is None:
        pestpp_opts = {}
    pst0.pestpp_options.update(pestpp_opts)

    # Write modified pest file
    pst0.write(pst_file1)

    # Run sensitivity analysis
    launch_pestpp(pst_file=pst_file1, pestpp_folder=pestpp_folder,
                  pestpp_cmd='pestpp-sen', parallel=parallel)
    return


def linear_uncertainty(analysis, pst_file0, pst_file1, pestpp_folder,
                       predictions=None):
    """Carry linear uncertainty calculations.

    Args:
        analysis: Type of predictive uncertainty analysis. It can take
            the values 'schur', for Schur's complement analysis for
            conditional uncertainty propagation; 'err_var', for error
            variance analysis; or 'prior', prior uncertainty estimation.
        pst_file0: Path of the original pest file.
        pst_file1: Path of the modified pest file.
        pestpp_folder: folder containing the PEST++ executables.
        predictions: list of predictions names. If None, predictions are
            read from the `pst_file0` as the observations with null
            weight.

    Returns:
        A :class:`LinearAnalysis` object (``analysis='prior'``),
        a :class:`Schur` object (``analysis='schur'``) or an
        :class:`ErrVar` object (``analysis='err_var'``).
        A modified PEST control file
        (`pst_file1`) and a Jacobian matrix file are also
        created file in the process.

    Note:
        It is supposed that the model has already been calibrated.
        Thus, the original PEST control file `pst_file0`
        should be in the same folder as the files created
        during the calibration process.

    References:
        * Doherty, J. (2010) *Methodologies and Software for PEST-Based
          Model Predictive Uncertainty Analysis.* Watermark Numerical
          Computing. 157 p.
        * White, J.T.; Fienen, M.N.; Doherty, J.E. (2016) A python
          framework for environmental model uncertainty analysis.
          *Environmental Modelling & Software*, 85, 217-228.
    """
    # load pest file
    pst0 = pyemu.Pst(pst_file0)

    # adjust weights
    pst0.control_data.noptmax = 0
    pst0.write(pst_file1)
    launch_pestpp(pst_file=pst_file1, pestpp_folder=pestpp_folder,
                  pestpp_cmd='pestpp-glm')
    pst1 = pyemu.Pst(pst_file1)
    pst1.adjust_weights_discrepancy()

    # calculate Jacobian matrix
    pst1.control_data.noptmax = -1
    pst1.write(pst_file1)
    launch_pestpp(pst_file=pst_file1, pestpp_folder=pestpp_folder,
                  pestpp_cmd='pestpp-glm')
    jco_file = pst_file1.rsplit('.', 1)[0] + '.jcb'

    # create LinearAnalysis object
    if predictions is None:
        predictions = pst1.zero_weight_obs_names
    if analysis == 'schur':
        # Schur's complement object
        la = pyemu.Schur(jco=jco_file, predictions=predictions)
    elif analysis == 'err_var':
        # error variance analysis object
        la = pyemu.ErrVar(jco=jco_file, predictions=predictions)
    elif analysis == 'prior':
        # linear analysis object (for prior uncertainty analyses only)
        la = pyemu.LinearAnalysis(jco=jco_file, predictions=predictions)
    else:
        raise KeyError('Type of analysis not recognised.')

    return la
