import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from cuspy import linear_uncertainty


register_matplotlib_converters()

# Set folders
pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'sphinx-doc/source/pyplots')
else:
    folder0 = whereami
os.chdir(folder0)

# Create Schur object
pred = ['temp_2015{:02d}01'.format(i) for i in np.arange(1, 13)] +\
    ['temp_2015{:02d}15'.format(i) for i in np.arange(1, 13)]
pred.sort()
la = linear_uncertainty(analysis='schur', pst_file0='pest4b.pst',
                        pst_file1='pest5.pst', pestpp_folder=pestpp_folder,
                        predictions=pred)

# Reduction in parameter uncertainty
ps = la.get_parameter_summary()

# Forecast summary
fs = la.get_forecast_summary()

# Residuals and forecasts
res = la.pst.res

# Read data for Figure
folder = '/nfs/alamode/Donnees_test/NAU48/'
meteo = pd.read_csv(os.path.join(folder, 'meteo.csv'), parse_dates=[0])

tw = pd.read_csv(os.path.join(folder, 'model_fld_tempSAT_b.wtr'), sep=';',
                 parse_dates=[0])
ind = np.in1d(meteo['time'], tw['time'])
ind2 = tw['time'] <= np.datetime64('2015-12-31')

# Plot posterior uncertainty
t_vec = [np.datetime64('2015-{:02d}-01'.format(i)) for i in np.arange(1, 13)] +\
    [np.datetime64('2015-{:02d}-15'.format(i)) for i in np.arange(1, 13)]
t_vec.sort()

post_sd = [np.sqrt(la.posterior_prediction[k]) for k in la.posterior_prediction]
post_sd = np.array(post_sd)

twest = res.loc[pred, 'modelled']

plt.figure()
plt.plot(t_vec, twest, 'k-')
plt.plot(t_vec, twest+2*post_sd, 'k--')
plt.plot(t_vec, twest-2*post_sd, 'k--')
plt.xlabel('Date')
plt.ylabel('Water temperature (ºC)')
plt.title('Posterior parametric uncertainty of simulations during 2015')
plt.savefig('fig5a.png')
plt.close()

# Plot percent reduction in forecast uncertainty by parameter
df = la.get_par_contribution()
df_percent = 100*(df.loc['base', :]-df)/df.loc['base', :]
df_percent = df_percent.iloc[1:, :]  # drop base column
ax = df_percent.T.plot(kind='bar', ylim=[0, 100])
ax.grid()
plt.xlabel('Date')
plt.ylabel('Percent uncertainty reduction')
plt.title('Percent uncertainty reduction by parameter and date')
plt.legend([r'$\alpha$', r'$\beta$', r'$\gamma$', r'$\mu$'])
plt.savefig('fig5b.png')

# Data worth
df2 = la.get_removed_obs_importance()
df2 = 100*(df2 - df2.loc['base', :])/df2

plt.figure(figsize=[6.4, 7])
plt.subplot(1, 2, 1)
plt.barh(df2.index, df2.loc[:, 'temp_20150101'])
plt.xlabel('Percent uncertainty increase if measurement not used')
plt.title('2015-01-01')
plt.xlim([0, 50])
plt.subplot(1, 2, 2)
plt.barh(df2.index, df2.loc[:, 'temp_20150701'])
plt.xlabel('Percent uncertainty increase if measurement not used')
plt.title('2015-07-01')
plt.xlim([0, 50])
plt.subplots_adjust(wspace=0.4)
plt.savefig('fig5c.png')
plt.close()
