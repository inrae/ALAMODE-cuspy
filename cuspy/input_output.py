"""Functions to read and write data.

The functions in this module are used to manage reading and writing of
input and output files.

This module contains the following functions:

- :func:`get_obs_data`: Get observation data.
- :func:`process_sweep_out`: Process file :file:`sweep_out.csv`.
- :func:`write_dict`: Write dictionary to file.
- :func:`write_dummy_pred_file`: Write a predictions file with dummy values.
- :func:`write_ins_file`: Write PEST instruction file.
- :func:`write_pest_files`: Writes PEST files.
- :func:`write_par_data_file`: Write parameter data file.
- :func:`write_tpl_file`: Write PEST template parameter file.

"""
# Copyright 2020-2023 Segula Technologies - Office Français de la Biodiversité.
#
# This file is part of the Python package "cuspy".
#
# The package "cuspy" is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The package "cuspy" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "cuspy".  If not, see <https://www.gnu.org/licenses/>.
import os
from datetime import datetime

import numpy as np
import pandas as pd
import pyemu


def get_obs_data(obs_file, start_date, end_date, weights=1, groups='obs',
                 obsnames='default', delimiter=' '):
    """Get observation data

    This function is used to read data (observations or predictions)
    from a file. It is also used to group data and to assign names and
    weights to data. In PEST parlance "observations" correspond to
    measurements already made (usually with weight > 0), and
    "predictions" (or "forecasts") correspond to data we intend to
    forecast (with weight = 0).

    Args:
        obs_file: path of the observations file (it should have the same
            format as the model output file). Missing values may be
            indicated with NA, na or NaN. The first column contains
            dates in the format "YYYY-mm-dd".
        start_date: date of start of simulation (in the format
            "YYYY-mm-dd").
        end_date: date of end of simulation (in the format
            "YYYY-mm-dd").
        weights: str or float. If str, it indicates the path to a file
            with the same format and column names as obs_file containing
            weights for each measurement. If float, it indicates a
            weight to apply to all measurements.
        groups: it can be a path, a string or 'default'. If it is a
            path, group names are read from a file with the same format
            and column names as obs_file. If 'default', observations are
            grouped by variable name. If another str, all observations
            are assigned to the same group.
        obsnames: it can be a path, a string or 'default'. If it is a
            path, observation names are read from a file with the same
            format and column names as obs_file. If 'default',
            observations names have the format xxxx_YYYYmmdd (xxxx is the
            corresponding variable name, and YYYYmmdd is a date string).
            If another str, the observation names have the format
            obsnamesNN, where NN is the index of the observation in the
            resulting dataframe.
        delimiter: column delimiter used in the files read by the
            function.

    Returns:
        A pandas dataframe containing the row and column indexes of
        observations in the output file, the observation names and
        groups, and their weights.
    """
    # Read observations data
    obs_data = pd.read_csv(obs_file, delimiter=delimiter,
                           parse_dates=[0])
    colnames = obs_data.columns.to_list()

    # Find row indexes
    datevec = pd.date_range(start_date, end_date)
    row_inds = np.where(np.in1d(datevec, obs_data.iloc[:, 0]))[0]
    obs_data.loc[:, 'row_ind'] = row_inds

    # Find column indexes
    obs_data2 = pd.melt(obs_data, id_vars=[colnames[0], 'row_ind'])
    obs_data2.loc[:, 'col_ind'] = obs_data2.loc[:, 'variable'].\
        replace(to_replace=colnames[1:],
                value=np.where(np.in1d(colnames, colnames[1:]))[0])

    # Add observation names
    if obsnames == 'default':
        obs_data2.loc[:, 'obsname'] = obs_data2.loc[:, 'variable'] + \
                                      '_' + obs_data2.iloc[:, 0].dt. \
                                      strftime('%Y%m%d')
    elif os.path.isfile(obsnames):
        obsnames_data = pd.read_csv(obsnames, delimiter=delimiter,
                                    parse_dates=[0])
        obsnames_data2 = pd.melt(obsnames_data, id_vars=[colnames[0]])
        obs_data2.loc[:, 'obsname'] = obsnames_data2.loc[:, 'value']
    else:
        obs_data2.loc[:, 'obsname'] = \
            [obsnames + str(i) for i in obs_data2.index]

    # Assign weights
    if isinstance(weights, str):
        weights_data = pd.read_csv(weights, delimiter=delimiter,
                                   parse_dates=[0])
        weights_data2 = pd.melt(weights_data, id_vars=[colnames[0]])
        obs_data2.loc[:, 'weight'] = weights_data2.loc[:, 'value']
    else:
        obs_data2.loc[:, 'weight'] = weights

    # Assign to groups
    if groups == 'default':
        obs_data2.loc[:, 'obsgroup'] = obs_data2.loc[:, 'variable']
    elif os.path.isfile(groups):
        groups_data = pd.read_csv(groups, delimiter=delimiter,
                                  parse_dates=[0])
        groups_data2 = pd.melt(groups_data, id_vars=[colnames[0]])
        obs_data2.loc[:, 'obsgroup'] = groups_data2.loc[:, 'value']
    else:
        obs_data2.loc[:, 'obsgroup'] = groups

    # Remove rows with missing data
    obs_data3 = obs_data2.dropna()

    return obs_data3


def process_sweep_out(fname_in, var_names, folder_out, ptl_avg=None):
    """Process file :file:`sweep_out.csv`.

    Args:
        fname_in: Path of the :file:`sweep_out.csv` file, created when
            making Monte Carlo simulations.
        var_names: List of variable names.
        folder_out: Folder where the processed data will be written.
        ptl_avg: Dictionary of variable names for which partial averages
            will be calculated. The keys indicate the variables used to
            group data into percentiles; the values are lists of
            variables names for which partial averages will be
            calculated for each of the percentile groups of
            the key variable.

    Returns:
        A series of text files containing the base simulation, the
        minimum, maximum, and the
        percentiles 5%, 25%, 50%, 75% and 95% of the simulations
        in the :file:`sweep_out.csv` file. The names of the output files
        follow the pattern "mc_uncert_<v>.txt", where `v` is the name of
        the output variable as used in :file:`sweep_out.csv`.
        In addition, if `ptl_avg` is specified, another series of files
        is created, which contains the partial averages of one variable
        (`vpa`) by percentile group of another variable (`v`). In this
        case, the output files follow the pattern
        "mc_pavg_<vpa>_by_<v>.txt".
    """
    # read only first line to get dtypes
    mc_res0 = pd.read_csv(fname_in, na_values=-1e10, nrows=1)
    res_dtypes = mc_res0.dtypes
    # manually assign dtypes to avoid warning about mixed dtypes later
    res_dtypes[:] = np.float64
    res_dtypes.run_id = np.int64
    res_dtypes.failed_flag = np.int64
    if "input_run_id" in res_dtypes:
        res_dtypes.input_run_id = "str"
    elif "Unnamed: 0" in res_dtypes:
        res_dtypes["Unnamed: 0"] = "str"
    res_dtypes = res_dtypes.to_dict()

    # read sweep_out.csv file
    mc_results = pd.read_csv(fname_in, na_values=-1e10, dtype=res_dtypes)
    # get observation names
    a_list = ['run_id', 'input_run_id', 'failed_flag', 'phi', 'meas_phi',
              'regul_phi'] + var_names
    colnames = list(mc_results.columns)
    prednames = [c for c in colnames if c not in a_list]

    # process data
    for v in var_names:
        var_preds = [p for p in prednames if p.startswith(v+'_')]
        npreds = len(var_preds)
        v_df = pd.DataFrame(index=range(npreds),
                            columns=['time', 'min', 'max',
                                     'p05', 'p25', 'p50', 'p75', 'p95'])
        for i in range(npreds):
            pred = var_preds[i]
            date_str = datetime.strptime(pred.replace(v+'_', ''), '%Y%m%d')
            date_str = date_str.strftime('%Y-%m-%d')
            v_df.loc[i, 'time'] = date_str
            v_df.loc[i, 'min'] = mc_results[pred].min(skipna=True)
            v_df.loc[i, 'max'] = mc_results[pred].max(skipna=True)
            for p in [5, 25, 50, 75, 95]:
                cname = f'p{p:02d}'
                v_df.loc[i, cname] = mc_results[pred].quantile(p/100)

        # write to file
        fname_out = os.path.join(folder_out, 'mc_uncert_' + v + '.txt')
        v_df.to_csv(fname_out, index=False, sep=' ')

        # calculate partial averages if necessary and write to file
        if ptl_avg:
            if v in ptl_avg:
                for vpa in ptl_avg[v]:
                    vpa_df = pd.DataFrame(
                        index=range(npreds),
                        columns=['time', 'p05', 'p25', 'p50', 'p75', 'p95'])
                    var_pa = [p for p in prednames if p.startswith(vpa + '_')]
                    for i in range(npreds):
                        # calculate partial averages by percentile group
                        vpa_df.loc[i, 'time'] = v_df.loc[i, 'time']
                        vpa_str = '_'.join([vpa, v_df.loc[i, 'time']]).replace('-', '')
                        if vpa_str in var_pa:
                            mc_data = mc_results[[var_preds[i], vpa_str]]
                            nreps = mc_data.shape[0]
                            mc_data.columns = ['var', 'vpa']
                            mc_data = mc_data.sort_values(by='var').reindex(range(nreps))
                            bins = [0, 0.05, 0.25, 0.50, 0.75, 0.95]
                            vpa_df.loc[i, ['p05', 'p25', 'p50', 'p75', 'p95']] = \
                                mc_data['vpa'].groupby(pd.qcut(mc_data.index, bins)).mean().values
                        else:
                            vpa_df.loc[i, ['p05', 'p25', 'p50', 'p75', 'p95']] = \
                                [np.nan]*5
                    # write to file
                    fname_out = os.path.join(
                        folder_out, 'mc_pavg_' + vpa + '_by_' + v + '.txt')
                    vpa_df.to_csv(fname_out, index=False, sep=' ')

    return


def write_dict(x_dict, path):
    """Write dictionary to file.

    This function writes a Python dictionary to a file. The file is
    organised in two columns, the first containing keys, and the second
    one containing values.

    Args:
        x_dict: a Python dictionary.
        path: path of the text file to write the data.

    Returns:
        A file located at `path` where the dictionary data is written.
    """
    with open(path, 'wt') as f:
        for k, v in x_dict.items():
            f.write(k + ' ' + str(v) + '\n')
    return


def write_dummy_pred_file(fname, time_stamps, colnames, time_colname='date',
                          dummy_value=0, sep=' '):
    """Write predictions file filled with dummy values.

    Args:
        fname: File name.
        time_stamps: List or array of time stamps corresponding to the
            data in the predictions file.
        colnames: Nomes of the columns in the predictions file.
        time_colname: Name of the column containing time data (provided
            through the argument `time_stamps`.
        dummy_value: Value used to fill the predictions file (except
            time data).
        sep: Column separator of the output file.

    Returns:
        A file with the same format as the output file, filled with
        dummy values.

    Note:
        A predictions file filled with dummy values may be useful when
        it is necessary to obtain simulation results for a certain
        period and there are no observations available.
    """
    other_colnames = list(set(colnames) - {time_colname})

    # Create empty DataFrame
    pred_data = pd.DataFrame(columns=colnames)

    # Fill DataFrame
    pred_data[time_colname] = time_stamps
    pred_data[other_colnames] = dummy_value

    # Write DataFrame to file
    pred_data.to_csv(fname, sep=sep, index=False)
    return


def write_ins_file(fname, obs_inds, pred_inds, ncols, nl_header=1,
                   field_wd=10, delimiter=' '):
    """Write PEST instruction file.

    This function is used to write a PEST(++) instruction file, a text
    file used to specify how PEST should read a model's output file.
    Detailed instructions on how to format an instructions file can be
    found in White et al. (2019).

    Args:
        fname: a file name. It is recommended to use the extension .ins.
        obs_inds: list of tuples (x, y, obsname) indicating the row
            index (x), column index (y) and name (obsname)
            corresponding to observations in the model output file.
        pred_inds: list of tuples (x, y, obsname) indicating the row
            index (x), column index (y) and name (obsname)
            corresponding to predictions in the model output file.
        ncols: number of columns of the output file.
        nl_header: number of lines of the file header.
        field_wd: width of the field in characters. It must be at least as
            long as the observation/prediction name.
        delimiter: delimiter character used in the output file.

    Returns:
        A PEST(++) instruction file (a text file specifying how to
        process a model output file to read the simulation results
        corresponding to the observations and predictions of interest).

    References:
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    # make sure obs_inds and pred_inds are numpy arrays
    obs_inds = np.array(obs_inds,
                        dtype=[('x', int), ('y', int),
                               ('obsname', '<U' + str(field_wd))])
    pred_inds = np.array(pred_inds,
                         dtype=[('x', int), ('y', int),
                                ('obsname', '<U' + str(field_wd))])

    # check there is no overlapping between observations and predictions
    if not set(map(tuple, obs_inds[['x', 'y']])).\
            isdisjoint(map(tuple, pred_inds[['x', 'y']])):
        raise ValueError('Observations and predictions have elements in ' +
                         'common.')

    # join obs_inds and pred_inds
    all_inds = np.concatenate([obs_inds, pred_inds])
    all_inds.sort(axis=0, order=['x', 'y', 'obsname'])

    # reorganise observations data
    j_list = np.unique(all_inds['x']).tolist()
    n_lines = len(j_list)
    v_list = []
    o_list = []
    for i in range(n_lines):
        v_list += [[]]
        o_list += [[]]
    n_obs = len(all_inds)
    ln = 0
    x_old = all_inds['x'][0]
    for i in range(n_obs):
        x_val = all_inds['x'][i]
        if x_val != x_old:
            ln += 1
        v_list[ln] += [all_inds['y'][i]]
        o_list[ln] += [all_inds['obsname'][i]]
        x_old = x_val

    # write file
    f = open(fname, 'w')
    f.write('pif @\n')
    for i in range(n_lines):
        if i == 0:
            f.write('l' + str(j_list[i] + nl_header + 1))
        else:
            f.write('l' + str(j_list[i] - j_list[i-1]))
        for k in range(ncols):
            if k in v_list[i]:
                ind = v_list[i].index(k)
                f.write(' !' + o_list[i][ind] + '!')
            elif k == 0:
                pass
            else:
                f.write(' !dum!')
            if k != ncols - 1:
                f.write(' @' + delimiter + '@')
        f.write('\n')
    f.close()
    return


def write_par_data_file(parnme, parval1, parlbnd, parubnd, partrans='none',
                        parchglim='relative', pargp=None, scale=1.0,
                        offset=0.0, dercom=1, file_path='par_data.csv'):
    """Write parameter data file.

    Args:
        parnme: List of names of the parameters.
        parval1: List of initial values of the parameters.
        parlbnd: List of lower bounds of the parameters.
        parubnd: List of upper bounds of the parameters.
        partrans: Transformation applied to all the parameters or list
            of transformations applied to each parameter. The possible
            values are "none", "log", "fixed" or "tied".
        parchglim: Type of parameter change limit (value to apply to all
            the parameters or list of values). The possible values are:
            "relative" and "factor".
        pargp: List of parameter group names. If None, the parameter
            group names are the same as the parameter names (one
            parameter group for each parameter).
        scale: Multiplier of list of multipliers of the parameter
            values.
        offset: Offset or list of offsets to aplly to the parameter
            values.
        dercom: Number (or list of numbers) of the command line used
            to calculate the derivatives of the parameters. It is
            usually equal to 1.
        file_path: Path of the parameter data file where the data will
            be written.
    """
    if pargp is not None:
        pargp = parnme
    par_data = pd.DataFrame({'parnme': parnme,
                             'partrans': partrans,
                             'parchglim': parchglim,
                             'parval1': parval1,
                             'parlbnd': parlbnd,
                             'parubnd': parubnd,
                             'pargp': pargp, 'scale': scale,
                             'offset': offset, 'dercom': dercom})
    par_data.to_csv(file_path, index=False, sep=' ')
    return


def write_pest_files(start_date, end_date, model_command,
                     par_file='par.txt', output_file='output.txt',
                     par_data_file='par_data.txt',
                     obs_file=None, pred_file=None, obs_weights=1,
                     obs_groups='default', obs_names='default',
                     pred_groups='default', pred_names='default',
                     tpl_file='par.tpl', ins_file='res_file.ins',
                     pst_file='pest.pst',
                     control_data=None, svd_data=None, reg_data=None,
                     pestpp_opts=None, delimiter=' '):
    """Write PEST files

    The function :func:`write_pest_files` is used to write the files
    necessary to run programs of the PEST(++) suite. This includes the
    control file, instructions file and template parameter file.
    For more information on the files used by PEST++, please see White
    et al. (2019).

    Args:
        start_date: date of start of simulations in str format
            ('YYYY-mm-dd') or datetime-like format.
        end_date: date of end of simulations in str format
            ('YYYY-mm-dd') or datetime-like format.
        model_command: command used to run the model.
        par_file: path of the model's parameter file. It is written by
            the function using the parameter values in `par_data_file`.
        output_file: path of the model's output file.
        par_data_file: path of a file containing parameter data to
            configure the parameter section of the PEST control file.
        obs_file: path of the observations file. It has the same format
            as `output_file`.
        pred_file: path of the predictions file. It has the same format
            as `output_file`.
        obs_weights: weights assigned to observations. It can be str or
            float. If str, it indicates the path to a file with the same
            format and column names as `obs_file` containing
            weights for each measurement. If float, it indicates a
            weight to apply to all measurements.
        obs_groups: groups to which each observation is assigned.
            It can be a path, a string or 'default'. If it is a path,
            group names are read from a file with the same format and
            column names as `obs_file`. If 'default', observations are
            grouped by variable name. If another str, all observations
            are assigned to the same group.
        obs_names: observation names. It can be a path, a string or
            'default'. If it is a path, observation names are read from
            a file with the same format and column names as `obs_file`.
            If 'default', observation names have the format
            "xxxx_YYYYmmdd" (xxxx is the corresponding variable name,
            and YYYYmmdd is a date string). If another str, the
            observation names have the format "obs_namesNN", where NN is
            the index of the observation in the resulting dataframe.
        pred_groups: groups to which each prediction is assigned.
            It can be a path, a string or 'default'. If it is a path,
            group names are read from a file with the same format and
            column names as `obs_file`. If 'default', predictions are
            grouped by variable name. If another str, all predictions
            are assigned to the same group.
        pred_names: prediction names. It can be a path, a string or
            'default'. If it is a path, prediction names are read from
            a file with the same format and column names as `pred_file`.
            If 'default', prediction names have the format
            "xxxx_YYYYmmdd" (xxxx is the corresponding variable name,
            and YYYYmmdd is a date string). If another str, the
            prediction names have the format "pred_namesNN", where NN is
            the index of the prediction in the resulting dataframe.
        tpl_file: path of the template parameter file. It is written by
            the function using the parameter names in `par_data_file`.
        ins_file: path of the pest instruction file. It is written by
            the function by using the data in `obs_file` and `pred_file`.
        pst_file: path of the PEST control file. It is written by the
            function using the data it has been passed to it.
        control_data: a dictionary defining options in the control data
            section of the PEST control file.
        svd_data: a dictionary used to pass options to the SVD section
            of the PEST control file.
        reg_data: a dictionary used to pass options to the
            regularization section of the PEST control file.
        pestpp_opts: a dictionary used to pass PEST++ options to the
            PEST control file.
        delimiter: delimiter character used in the `output_file`,
            `obs_file` and `pred_file`.

    Returns:
        A series of PEST files (control file, instructions file and
        template parameter file) and a parameter file.

    References:
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    # Read data
    # ---------
    # Read parameter data
    par_data = pd.read_csv(par_data_file, delimiter=' ')
    par_data.index = par_data.loc[:, 'parnme']
    par_names = par_data['parnme']

    # Read observation data
    if (obs_file is None) & (pred_file is None):
        raise ValueError('obs_file and pred_file cannot both be None.')
    if obs_file is not None:
        obs_data = get_obs_data(obs_file=obs_file,
                                start_date=start_date, end_date=end_date,
                                weights=obs_weights, groups=obs_groups,
                                obsnames=obs_names,
                                delimiter=delimiter)
    if pred_file is not None:
        pred_data = get_obs_data(obs_file=pred_file,
                                 start_date=start_date, end_date=end_date,
                                 weights=0, groups=pred_groups,
                                 obsnames=pred_names, delimiter=delimiter)
    if (obs_file is not None) & (pred_file is not None):
        all_data = pd.concat([obs_data, pred_data])
    elif obs_file is not None:
        all_data = obs_data
    elif pred_file is not None:
        all_data = pred_data
    all_names = all_data['obsname']

    # Write auxiliary PEST files
    # --------------------------
    # Write pest template parameter file
    write_tpl_file(tpl_file, par_names)

    # Write pest instruction file
    ncols = 1
    if obs_file is not None:
        obs_inds = list(map(tuple, obs_data.
                            loc[:, ['row_ind', 'col_ind', 'obsname']].
                            to_numpy()))
        ncols = np.max([ncols, np.max(obs_data['col_ind']) + 1])
    else:
        obs_inds = []
    if pred_file is not None:
        pred_inds = list(map(tuple, pred_data.
                             loc[:, ['row_ind', 'col_ind', 'obsname']].
                             to_numpy()))
        ncols = np.max([ncols, np.max(pred_data['col_ind']) + 1])
    else:
        pred_inds = []
    write_ins_file(ins_file, obs_inds, pred_inds, ncols=ncols, field_wd=20,
                   delimiter=delimiter)

    # Pest control file
    # -----------------
    # Create generic pest instance
    pst1 = pyemu.pst.pst_utils.generic_pst(par_names=par_names,
                                           obs_names=all_names)
    # Add parameter data
    pst1.parameter_data = par_data

    # Add observations data
    pst1.observation_data.index = all_data['obsname']
    pst1.observation_data[['obsnme', 'obsval', 'weight', 'obgnme']] = \
        all_data[['obsname', 'value', 'weight', 'obsgroup']].to_numpy()

    # Add instruction to run the model
    pst1.model_command = [model_command]

    # Add file names
    pst1.template_files = [tpl_file]
    pst1.input_files = [par_file]
    pst1.instruction_files = [ins_file]
    pst1.output_files = [output_file]

    # Configure control data
    if control_data is not None:
        for k in control_data:
            pst1.control_data.__setattr__(k, control_data[k])

    # Configure SVD data
    if svd_data is not None:
        for k in svd_data:
            pst1.svd_data.__setattr__(k, svd_data[k])

    # Configure regularization data
    if reg_data is not None:
        for k in reg_data:
            pst1.reg_data.__setattr__(k, reg_data[k])

    # Add Pest++ options
    if pestpp_opts is not None:
        pst1.pestpp_options.update(pestpp_opts)

    # Check PEST file
    pst1.sanity_checks()

    # Write pest file
    pst1.write(pst_file)

    return


def write_tpl_file(fname, par_names):
    """Write PEST template parameter file.

    This function writes a PEST template parameter file, a text file
    used to specify the format of the parameter file. The parameter file
    is a text file where the values of the parameters used by the model
    are written.

    Args:
        fname: a file name. It is recommended to use the extension .tpl.
        par_names: list of parameter names in the order they appear in
            the parameter file.

    Returns:
        A PEST(++) template parameter file (a text file specifying the
        format of the parameter file).

    References:
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    f = open(fname, 'w')
    f.write('ptf #\n')
    for p in par_names:
        f.write('%s #%s       #\n' % (p, p))
    f.close()
    return
