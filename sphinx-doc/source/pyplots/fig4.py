import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pyemu

from cuspy import calibration, monte_carlo, gsa
from tributary import tmohseni_etal1998


# Set folders
pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'sphinx-doc/source/pyplots')
else:
    folder0 = whereami
os.chdir(folder0)

# Read and modify pest file
pest4 = pyemu.Pst('pest.pst')
pest4.parameter_data.loc[['par3', 'par4'],'partrans'] = 'fixed'
pest4.write('pest4.pst')

# Calibrate model using DE
calibration(method='de', pst_file0='pest4.pst', pst_file1='pest4.pst',
            pestpp_folder=pestpp_folder,
            pestpp_opts={'de_pop_size': 40, 'de_max_gen': 50})

# Read calibration results
par_cal = pd.read_csv('pest4.par', sep='\s+', skiprows=1, header=None)

# Read data for Figure
folder = '/nfs/alamode/Donnees_test/NAU48/'
meteo = pd.read_csv(os.path.join(folder, 'meteo.csv'), parse_dates=[0])

tw = pd.read_csv(os.path.join(folder, 'model_fld_tempSAT_b.wtr'), sep=';',
                 parse_dates=[0])
ind = np.in1d(meteo['time'], tw['time'])
ind2 = tw['time'] <= np.datetime64('2015-12-31')

# Plot figure
plt.figure()
ta = np.arange(0, 25, 0.1)
pars = par_cal.iloc[:, 1]
twest = tmohseni_etal1998(ta, pars)
plt.plot(ta, twest, 'c-')
plt.plot(meteo['AirTemp'][ind], tw['temp0.000'][ind2], 'k*')
plt.xlim([0, 25])
plt.ylim([0, 25])
plt.xlabel('Air temperature (ºC)')
plt.ylabel('Water temperature (ºC)')
textstr = '\n'.join(
    (r'$\alpha=%.2f$ ºC' % (pars[0]),
     r'$\beta=%.2f$ ºC' % (pars[1]),
     r'$\gamma=%.2f ºC^{-1}$' % (pars[2]),
     r'$\mu=%.2f$ ºC' % (pars[3]),
     '',
     r'$rmse=%.2f$ ºC' % (np.sqrt(283.219/46))))
plt.text(5, 16, textstr)
plt.title('Model calibrated by DE')
plt.savefig('fig4a.png')
plt.close()

pest4b = pyemu.Pst('pest4.pst')
pest4b.parrep('pest4.par')
pest4b.parameter_data.loc[:,'partrans'] = 'none'
pest4b.write('pest4b.pst')

# Calibrate again with GLM
calibration(method='glm', pst_file0='pest4b.pst', pst_file1='pest4b.pst',
            pestpp_folder=pestpp_folder)

# Read calibration results
pest4b.load('pest4b.pst')
pest4b.parrep('pest4b.par')
pest4b.resfile = 'pest4b.rei'
res_stats = pest4b.get_res_stats()

# Plot figure
plt.figure()
ta = np.arange(0, 25, 0.1)
pars = pest4b.parameter_data['parval1']
twest = tmohseni_etal1998(ta, pars)
plt.plot(ta, twest, 'c-')
plt.plot(meteo['AirTemp'][ind], tw['temp0.000'][ind2], 'k*')
plt.xlim([0, 25])
plt.ylim([0, 25])
plt.xlabel('Air temperature (ºC)')
plt.ylabel('Water temperature (ºC)')
textstr = '\n'.join(
    (r'$\alpha=%.2f$ ºC' % (pars[0]),
    r'$\beta=%.2f$ ºC' % (pars[1]),
    r'$\gamma=%.2f ºC^{-1}$' % (pars[2]),
    r'$\mu=%.2f$ ºC' % (pars[3]),
    '',
    r'$rmse=%.2f$ ºC' % (res_stats.loc['rmse', 'all'])))
plt.text(5, 16, textstr)
plt.title('Model calibration refined with GLM')
plt.savefig('fig4b.png')

# Monte Carlo and Regression analysis
pest4c = pyemu.Pst('pest4b.pst')
pest4c.parameter_data.loc['par3', 'parlbnd'] = 0
pest4c.parameter_data.loc['par4', 'parlbnd'] = -4
pest4c.write('pest4b.pst')
n_samples = 100
monte_carlo(pst_file0='pest4b.pst', pst_file1='pest4c.pst', dist_type='post',
            distribution='gaussian', n_samples=n_samples,
            pestpp_folder=pestpp_folder,
            csv_in='sweep_in4c.csv', parallel=False,
            pestpp_opts={'sweep_output_csv_file': 'sweep_out4c.csv'})

mc_results = pd.read_csv('sweep_out4c.csv')
mc_pars = pd.read_csv('sweep_in4c.csv')

r2 = []
for n_obs in range(pest4c.nnz_obs):
    v_sim = mc_results.loc[:, pest4c.nnz_obs_names[n_obs]]
    v_pars = mc_pars.iloc[:, 1:]
    reg = np.linalg.lstsq(v_pars, v_sim, rcond=None)
    ss_res = reg[1][0]
    ss_tot = np.sum((v_sim - np.mean(v_sim))**2)
    coef_det = 1 - ss_res/ss_tot
    r2 += [coef_det]
plt.figure()
# plt.hist(r2)
plt.subplot(1, 2, 1)
plt.plot(pest4c.observation_data.loc[pest4c.nnz_obs_names, 'obsval'], r2, '.')
plt.subplot(1, 2, 2)
plt.plot(r2, '.')
plt.savefig('fig4c.png')
np.sum(np.greater_equal(r2,  0.7))

v_sim = mc_results.loc[:, pest4c.nnz_obs_names[28]]
plt.figure()
for i in range(1, 5):
    var = 'par' + str(i)
    plt.subplot(2, 4, i)
    plt.plot(v_pars[var], v_sim, '.')
for i in range(1, 5):
    var = 'par' + str(i)
    plt.subplot(2, 4, i + 4)
    plt.hist(v_pars[var])
plt.savefig('fig4d.png')
