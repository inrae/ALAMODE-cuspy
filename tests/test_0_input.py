"""TEST 0: Test input and output functions.
"""
import os
from shutil import copyfile, rmtree

import numpy as np
import pandas as pd

import okplm.parameter_functions as pf
from okplm.parameter_constants import *
from okplm import read_dict

from cuspy import input_output as io


whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

data_folder = os.path.join(folder0, "../example_data")
folder = os.path.join(folder0, 'test0')
if os.path.isdir(folder):
    rmtree(folder)
os.mkdir(folder)
os.chdir(folder)

# ----------------------------------------------------------------------
# Test 0.1: write PEST instruction file
# ----------------------------------------------------------------------
# Write PEST instruction file (one variable)
obs_inds = [(0, 1, 'temp0'), (1, 1, 'temp1'), (3, 1, 'temp3')]
pred_inds = [(5, 1, 'temp5'), (6, 1, 'temp6')]
io.write_ins_file('test.ins', obs_inds, pred_inds, ncols=2)

# Write PEST instruction file (two variables)
obs_inds = [(0, 1, 'tepi0'), (0, 2, 'thyp0'), (1, 1, 'tepi1'), (3, 2, 'thyp3')]
pred_inds = [(5, 2, 'thyp5p'), (6, 1, 'tepi6p'), (6, 2, 'thyp6p')]
io.write_ins_file('test.ins', obs_inds, pred_inds, ncols=3)

# Check a ValueError is raised when there are repeated values
obs_inds = [(0, 1, 'tepi0'), (0, 2, 'thyp0'), (1, 1, 'tepi1'), (3, 2, 'thyp3')]
pred_inds = [(0, 2, 'thyp0p'), (5, 2, 'thyp5p'), (6, 1, 'tepi6p'),
             (6, 2, 'thyp6p')]
try:
    io.write_ins_file('test.ins', obs_inds, pred_inds, ncols=3)
except ValueError:
    pass

# ----------------------------------------------------------------------
# Test 0.2: read observation data
# ----------------------------------------------------------------------
obs_file = os.path.join(data_folder, 'obs.txt')
start_date = '1970-01-01'
end_date = '2015-12-31'
# weights = 1
weights = os.path.join(data_folder, 'obs_weights.txt')
# groups = 'obs'
# groups = 'default'
groups = os.path.join(data_folder, 'obs_groups.txt')
# obsnames = 'default'
obsnames = 't'
# obsnames = os.path.join(data_folder, 'obs_names.txt')
delimiter = ' '

obs_props = io.get_obs_data(obs_file=obs_file, start_date=start_date,
                            end_date=end_date, weights=weights, groups=groups,
                            obsnames=obsnames, delimiter=delimiter)

# ----------------------------------------------------------------------
# Test 0.3: write PEST files
# ----------------------------------------------------------------------
# Copy data to folder
copyfile(os.path.join(data_folder, 'lake.txt'),
         os.path.join(folder, 'lake.txt'))
copyfile(os.path.join(data_folder, 'obs.txt'),
         os.path.join(folder, 'obs.txt'))
copyfile(os.path.join(data_folder, 'pred.txt'),
         os.path.join(folder, 'pred.txt'))
copyfile(os.path.join(data_folder, 'meteo.txt'),
         os.path.join(folder, 'meteo.txt'))

# Read data
meteo_data = pd.read_csv(os.path.join(data_folder, 'meteo.txt'), delimiter=' ',
                         parse_dates=[0])
tair = meteo_data['tair']
start_date = meteo_data['date'][0]
end_date = meteo_data['date'].iloc[-1]

lake_data = read_dict(os.path.join(folder, 'lake.txt'))

# Derived variables
par_cts = {'ALPHA1': ALPHA1, 'ALPHA2': ALPHA2,
           'ALPHA3': ALPHA3, 'ALPHA4': ALPHA4,
           'BETA1': BETA1, 'BETA2': BETA2, 'BETA3': BETA3,
           'A1': A1, 'A2': A2, 'A3': A3, 'A4': A4,
           'B1': B1, 'B2': B2,
           'C1': C1, 'C2': C2,
           'D': D}
if lake_data['type'] == 'R':
    # Reservoirs (submerged outlet)
    par_cts.update({'E1': E1_RES, 'E2': E2_RES,
                    'E3': E3_RES})
elif lake_data['type'] == 'L':
    # Lakes (surface outlet)
    par_cts.update({'E1': E1_LAKE, 'E2': E2_LAKE,
                    'E3': E3_LAKE})
a_est = pf.estimate_par_a(var_vals=lake_data, par_cts=par_cts)
b_est = pf.estimate_par_b(var_vals=lake_data, par_cts=par_cts)
c_est = pf.estimate_par_c(var_vals=lake_data, par_cts=par_cts)
d_est = par_cts['D']
e_est = pf.estimate_par_e(var_vals=lake_data, par_cts=par_cts)
alpha_est = pf.estimate_par_alpha(var_vals=lake_data, par_cts=par_cts)
beta_est = pf.estimate_par_beta(par_e=e_est, par_cts=par_cts)
mat_est = np.mean(tair)
at_factor_est = 1.0
sw_factor_est = 1.0

par_vals_est = {'A': a_est, 'B': b_est, 'C': c_est, 'D': d_est, 'E': e_est,
                'ALPHA': alpha_est, 'BETA': beta_est, 'mat': mat_est,
                'at_factor': at_factor_est, 'sw_factor': sw_factor_est}
par_names = list(par_vals_est.keys())

# Write parameter files
io.write_dict(par_vals_est, os.path.join(folder, 'par.txt'))

par_data = pd.DataFrame({'parnme': par_names,
                         'partrans': ['none']*8 + ['fixed']*2,
                         'parchglim': 'relative',
                         'parval1': [a_est, b_est, c_est, d_est, e_est,
                                     alpha_est, beta_est, mat_est,
                                     at_factor_est, sw_factor_est],
                         'parlbnd': [a_est - 2*0.74, b_est - 2*0.08,
                                     c_est - 2*0.004, 0, 0, 0, 0,
                                     mat_est - 2*0.5, 0.9, 0.9],
                         'parubnd': [a_est + 2*0.74, b_est + 2*0.08,
                                     c_est + 2*0.004, 1, 1,
                                     alpha_est + 2*0.08, 1,
                                     mat_est + 2*0.5, 1.1, 1.1],
                         'pargp': par_names, 'scale': 1.0,
                         'offset': 0.0, 'dercom': 1})
# parameter values and bounds based on Prats & Danis (2019)
par_data.to_csv(os.path.join(folder, 'par_data.csv'), index=False, sep=' ')

# Write pest files
# ----------------
io.write_pest_files(start_date=start_date, end_date=end_date,
                    tpl_file='par.tpl', par_file='par.txt',
                    par_data_file='par_data.csv', obs_file='obs.txt',
                    pred_file='pred.txt', ins_file='res_file.ins',
                    output_file='output.txt', pst_file='test0.pst',
                    model_command='run_okp',
                    control_data={'noptmax': 0, 'numlam': 10},
                    svd_data={'maxsing': len(par_names)})

# Delete unnecessary files and go back to initial work directory
os.remove('test.ins')
os.chdir(folder0)
