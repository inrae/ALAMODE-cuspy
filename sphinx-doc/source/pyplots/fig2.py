import os
import time

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pyemu

from cuspy import monte_carlo, write_pest_files, write_dict


n_samples = 500

# Set folders
pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'sphinx-doc/source/pyplots')
else:
    folder0 = whereami
os.chdir(folder0)

# Read data
folder = '/nfs/alamode/Donnees_test/NAU48/'
meteo = pd.read_csv(os.path.join(folder, 'meteo.csv'), parse_dates=[0])

tw = pd.read_csv(os.path.join(folder, 'model_fld_tempSAT_b.wtr'), sep=';',
                 parse_dates=[0])

# Prepare simulation input files
ind3 = meteo['time'] >= np.datetime64('1999-01-01')
meteo[['time', 'AirTemp']][ind3].to_csv('meteo.txt', index=False, sep=' ',
                                        header=['time', 'Ta_mean'])

tr_file_data = {'par1': 26.2, 'par2': 13.3, 'par3': 0.18, 'par4': 0.8}
write_dict(tr_file_data, 'tributary.txt')

# Prepare PEST files
# ------------------
# par_data
par_data = pd.DataFrame({'parnme': ['par1', 'par2', 'par3', 'par4'],
                         'partrans': ['none']*4,
                         'parchglim': 'relative',
                         'parval1': [26.2, 13.3, 0.18, 0.8],
                         'parlbnd': [10.8, 3.7, 0.1, 0.0],
                         'parubnd': [40.9, 20.8, 0.8, 8.9],
                         'pargp': ['par1', 'par2', 'par3', 'par4'],
                         'scale': 1.0,
                         'offset': 0.0, 'dercom': 1})
par_data.to_csv('par_data.csv', index=False, sep=' ')

# obs_file
ind = tw['time'] <= np.datetime64('2014-12-31')
tw[['time', 'temp0.000']][ind].to_csv('obs.txt', header=['time', 'temp'],
                                      index=False, sep=',')

# pred_file
# ind2a = tw['time'] >= np.datetime64('2015-01-01')
# ind2b = tw['time'] <= np.datetime64('2015-12-31')
# ind2 = ind2a & ind2b
# tw[['time', 'temp0.000']][ind2].to_csv('pred.txt', header=['time', 'temp'],
#                                        index=False, sep=',')

t_vec = [np.datetime64('2015-{:02d}-01'.format(i)) for i in np.arange(1,13)] +\
    [np.datetime64('2015-{:02d}-15'.format(i)) for i in np.arange(1,13)]
t_vec.sort()
temp_vec = [0]*len(t_vec)

pred = pd.DataFrame(data={'time': t_vec, 'temp': temp_vec})
pred.to_csv('pred.txt', index=False, sep=',')

# model_command
model_command = 'run_tributary --noflow --temp 1'
write_pest_files(start_date='1999-01-01', end_date='2015-12-31',
                 par_file='tributary.txt',
                 par_data_file='par_data.csv', obs_file='obs.txt',
                 pred_file='pred.txt', obs_weights=1,
                 model_command=model_command, delimiter=',')

# Make Monte Carlo calculations
t0 = time.time()
monte_carlo(pst_file0='pest.pst', pst_file1='pest2.pst', dist_type='prior',
            distribution='uniform', n_samples=n_samples,
            pestpp_folder=pestpp_folder,
            csv_in='sweep_in.csv', parallel=False)
t1 = time.time()

# Read simulation results
mc_pars = pd.read_csv('sweep_in.csv')
mc_results = pd.read_csv('sweep_out.csv')

# Plot distribution of parameter values
plt.figure()
plt.subplot(2, 2, 1)
plt.hist(mc_pars['par1'])
plt.xlabel(r'$\alpha$ (ºC)')
plt.ylabel('N')

plt.subplot(2, 2, 2)
plt.hist(mc_pars['par2'])
plt.xlabel(r'$\beta$ (ºC)')
plt.ylabel('N')

plt.subplot(2, 2, 3)
plt.hist(mc_pars['par3'])
plt.xlabel(r'$\gamma$ (º$C^{⁻1}$)')
plt.ylabel('N')

plt.subplot(2, 2, 4)
plt.hist(mc_pars['par4'])
plt.xlabel(r'$\mu$ (ºC)')
plt.ylabel('N')
plt.suptitle('Distribution of parameter values')
plt.savefig('fig2a.png')
plt.close()

# Prepare data for uncertainty plot
pred['t_50'] = 0
pred['t_95'] = 0
pred['t_05'] = 0
for i in range(len(pred)):
    col = 'temp_' + pred['time'][i].strftime('%Y%m%d')
    pred.loc[i, 't_50'] = mc_results[col].median()
    pred.loc[i, 't_05'] = mc_results[col].quantile(0.05)
    pred.loc[i, 't_95'] = mc_results[col].quantile(0.95)

# Plot uncertainty
plt.figure()
plt.plot(pred['time'], pred['t_50'], 'k-')
plt.plot(pred['time'], pred['t_05'], 'k--')
plt.plot(pred['time'], pred['t_95'], 'k--')
plt.xlabel('Date')
plt.ylabel('Temperature (ºC)')
plt.legend(['median', '5% percentile', '95% percentile'])
plt.title('Prior uncertainty of simulations during 2015')
plt.savefig('fig2b.png')
plt.close()

# Regression analysis
mc_results = pd.read_csv('sweep_out.csv')
mc_pars = pd.read_csv('sweep_in.csv')
pest2 = pyemu.Pst('pest2.pst')

r2 = []
for n_obs in range(pest2.nnz_obs):
    v_sim = mc_results.loc[:, pest2.nnz_obs_names[n_obs]]
    v_pars = mc_pars.iloc[:, 1:]
    reg = np.linalg.lstsq(v_pars, v_sim, rcond=None)
    ss_res = reg[1][0]
    ss_tot = np.sum((v_sim - np.mean(v_sim))**2)
    coef_det = 1 - ss_res/ss_tot
    r2 += [coef_det]
plt.figure()
plt.hist(r2)
# plt.savefig('fig2c.png')
np.sum(np.greater_equal(r2,  0.7))
