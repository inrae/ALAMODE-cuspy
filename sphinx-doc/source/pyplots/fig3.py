import os

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from cuspy import gsa
from tributary import tmohseni_etal1998


n_samples = 1000

# Set folders
pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'sphinx-doc/source/pyplots')
else:
    folder0 = whereami
os.chdir(folder0)

# Make sensitivity analysis calculations
gsa(method='sobol', pst_file0='pest.pst', pst_file1='pest3.pst',
    pestpp_folder=pestpp_folder,
    pestpp_opts={'gsa_sobol_samples': 50, 'gsa_sobol_par_dist': 'unif'},
    parallel=False,)

# Make sensitivity analysis calculations (larger sample)
gsa(method='sobol', pst_file0='pest.pst', pst_file1='pest3b.pst',
    pestpp_folder=pestpp_folder,
    pestpp_opts={'gsa_sobol_samples': 400, 'gsa_sobol_par_dist': 'unif'},
    parallel=False)

# Read data for Figure
folder = '/nfs/alamode/Donnees_test/NAU48/'
meteo = pd.read_csv(os.path.join(folder, 'meteo.csv'), parse_dates=[0])

tw = pd.read_csv(os.path.join(folder, 'model_fld_tempSAT_b.wtr'), sep=';',
                 parse_dates=[0])
ind = np.in1d(meteo['time'], tw['time'])
ind2 = tw['time'] <= np.datetime64('2015-12-31')

par_vals = pd.read_csv('pest3b.sobol.par.csv')

# Plot figure
plt.figure()
ta = np.arange(0, 25, 0.1)
for i in range(400):
    pars = par_vals.loc[i, ['par1', 'par2', 'par3', 'par4']]
    twest = tmohseni_etal1998(ta, pars)
    plt.plot(ta, twest, 'c-')
plt.plot(meteo['AirTemp'][ind], tw['temp0.000'][ind2], 'k*')
plt.xlim([0, 25])
plt.ylim([0, 25])
plt.xlabel('Air temperature (ºC)')
plt.ylabel('Water temperature (ºC)')
plt.savefig('fig3.png')
