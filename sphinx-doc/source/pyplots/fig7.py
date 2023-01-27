import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
import pandas as pd
import pyemu

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

# Read data
meteo = pd.read_csv('meteo.txt', sep=' ', parse_dates=[0])
inda = meteo['time'] >= np.datetime64('2015-01-01')
indb = meteo['time'] <= np.datetime64('2015-12-31')
ind = inda & indb
meteo.loc[ind, 'Ta_mean'] = meteo.loc[ind, 'Ta_mean'] + 1.5  # Prospective climate change effect
meteo.to_csv('meteo_t1_5.csv', index=False, sep=' ')

# Predictive error (only 1st and 15th day in each month)
t_vec = [np.datetime64('2015-{:02d}-01'.format(i)) for i in np.arange(1, 13)] +\
    [np.datetime64('2015-{:02d}-15'.format(i)) for i in np.arange(1, 13)]
t_vec.sort()
pred_names = ['temp_' + str(d).replace('-', '') for d in t_vec]
pred_names.sort()
pest7 = pyemu.Pst('pest4b.pst')
pest7.model_command = 'run_tributary --noflow --temp 1 -m meteo_t1_5.csv'
pest7.write('pest7.pst')
la_0 = linear_uncertainty(analysis='err_var', pst_file0='pest4b.pst',
                          pst_file1='pest6.pst', pestpp_folder=pestpp_folder,
                          predictions=pred_names)
la_1_5 = linear_uncertainty(analysis='err_var', pst_file0='pest7.pst',
                            pst_file1='pest7.pst', pestpp_folder=pestpp_folder,
                            predictions=pred_names)
res_0 = la_0.pst.res
twest_0 = res_0.loc[pred_names, 'modelled']
errvar_res_0 = la_0.get_errvar_dataframe(2)
post_var_0 = errvar_res_0['first'] + errvar_res_0['second'] + errvar_res_0['third']
post_sd_0 = np.sqrt(post_var_0.values[0])

res_1_5 = la_1_5.pst.res
twest_1_5 = res_1_5.loc[pred_names, 'modelled']
errvar_res_1_5 = la_1_5.get_errvar_dataframe(2)
post_var_1_5 = errvar_res_1_5['first'] + errvar_res_1_5['second'] + errvar_res_1_5['third']
post_sd_1_5 = np.sqrt(post_var_1_5.values[0])

plt.figure()
# plt.subplot(2, 1, 1)
plt.subplot2grid((3, 1), (0, 0), rowspan=2)
plt.plot(t_vec, twest_0, 'k-')
plt.plot(t_vec, twest_0+2*post_sd_0, 'k--')
plt.plot(t_vec, twest_0-2*post_sd_0, 'k--')
plt.plot(t_vec, twest_1_5, 'r-')
plt.plot(t_vec, twest_1_5+2*post_sd_1_5, 'r--')
plt.plot(t_vec, twest_1_5-2*post_sd_1_5, 'r--')
plt.ylabel('Water temperature (ºC)')
plt.legend(['Predictions', '2.5% interval of pred.', '97.5% interval of pred.',
            'Predictions (+1.5ºC)', '2.5% interval of pred. (+1.5ºC)',
            '97.5% interval of pred. (+1.5ºC)'])
plt.title(r'Posterior predictive error of simulations during 2015 and ' +
          r'climate change scenario $T_{air} + 1.5$ ºC')
# plt.subplot(2, 1, 2)
plt.subplot2grid((3, 1), (2, 0), rowspan=1)
plt.plot(t_vec, post_sd_0, 'k')
plt.plot(t_vec, post_sd_1_5, 'r')
plt.xlabel('Date')
plt.ylabel('Std. error of predictions (ºC)')
plt.ylim([0, 5])
plt.savefig('fig7.png')
plt.close()

print(np.mean(twest_1_5 - twest_0))