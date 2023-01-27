import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
import numpy as np
import pandas as pd
import pyemu

from cuspy import linear_uncertainty, write_pest_files


register_matplotlib_converters()
# Set folders
pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'sphinx-doc/source/pyplots')
else:
    folder0 = whereami
os.chdir(folder0)

# Create ErrVar object
pred = ['temp_2015{:02d}01'.format(i) for i in np.arange(1, 13)] +\
    ['temp_2015{:02d}15'.format(i) for i in np.arange(1, 13)]
pred.sort()
la = linear_uncertainty(analysis='err_var', pst_file0='pest4b.pst',
                        pst_file1='pest6.pst', pestpp_folder=pestpp_folder,
                        predictions=pred)

# Singular spectrum
s = la.qhalfx.s

plt.figure()
plt.subplot(1, 2, 1)
plt.plot([1, 2, 3, 4], s.x)
plt.hlines(0, 1, 4)
plt.hlines(4/np.sqrt(3)*np.median(s.x), 1, 4, colors='r', linestyles='dashed')
plt.annotate(r'$4/\sqrt{3}y_{med}$ threshold', xy=[2.5, 9])
plt.xlim([1, 4])
plt.title('Singular spectrum')
plt.ylabel('Power')
plt.xticks(ticks=[1, 2, 3, 4])

plt.subplot(1, 2, 2)
plt.plot([1, 2, 3, 4], np.cumsum(s.x)/np.sum(s.x)*100)
plt.hlines(90, 1, 4, colors='r', linestyles='dashed')
plt.annotate('90% energy threshold', xy=[2, 85])
plt.xlim([1, 4])
plt.ylim([0, 100])
plt.xlabel('Singular Value')
plt.ylabel('Cumulative energy')
plt.xticks(ticks=[1, 2, 3, 4])
plt.savefig('fig6a.png')
plt.close()

# Identifiability
pi = la.get_identifiability_dataframe(2)

plt.figure()
plt.bar(la.pst.par_names, pi['right_sing_vec_1'])
plt.bar(la.pst.par_names, pi['right_sing_vec_2'], bottom=pi['right_sing_vec_1'])
plt.xticks((0, 1, 2, 3),(r'$\alpha$', r'$\beta$', r'$\gamma$', r'$\mu$'))
plt.ylim([0, 1])
plt.ylabel('Identifiability')
plt.legend(['Singular value 1', 'Singular value 2'])
plt.title('Parameter identifiability')
plt.savefig('fig6b.png')

# Correlation
parcov = pyemu.Cov.from_ascii('pest6.post.cov').to_dataframe()
v = np.sqrt(np.diag(parcov))
outer_v = np.outer(v, v)
parcorr = parcov/outer_v

# Create ErrVar object
t_vec = np.datetime64('2015-01-01') + np.arange(365)
temp_vec = [0]*len(t_vec)
pred = pd.DataFrame(data={'time': t_vec, 'temp': temp_vec})
pred.to_csv('pred6.txt', index=False, sep=',')
model_command = 'run_tributary --noflow --temp 1'
write_pest_files(start_date='1999-01-01', end_date='2015-12-31',
                 par_file='tributary.txt',
                 par_data_file='par_data.csv', obs_file='obs.txt',
                 pred_file='pred6.txt', obs_weights=1,
                 model_command=model_command, delimiter=',',
                 pst_file='pest6b.pst', ins_file='res_file6.ins')

pred_names = ['temp_' + str(d).replace('-', '') for d in t_vec]
pred_names.sort()
la2 = linear_uncertainty(analysis='err_var', pst_file0='pest6b.pst',
                         pst_file1='pest6b.pst', pestpp_folder=pestpp_folder,
                         predictions=pred_names)

# Read data for plot
folder = '/nfs/alamode/Donnees_test/NAU48/'
tw = pd.read_csv(os.path.join(folder, 'model_fld_tempSAT_b.wtr'), sep=';',
                 parse_dates=[0])

ind3 = np.logical_and(tw['time'] >= np.datetime64('2015-01-01'),
                      tw['time'] <= np.datetime64('2015-12-31'))

res = la2.pst.res
twest = res.loc[pred_names, 'modelled']

errvar_res = la2.get_errvar_dataframe(2)
post_var = errvar_res['first'] + errvar_res['second'] + errvar_res['third']
post_sd = np.sqrt(post_var.values[0])

# Predictive error
plt.figure()
plt.plot(t_vec, twest, 'k-')
plt.plot(t_vec, twest+2*post_sd, 'k--')
plt.plot(t_vec, twest-2*post_sd, 'k--')
plt.plot(tw['time'][ind3], tw['temp0.000'][ind3], 'r*')
plt.xlabel('Date')
plt.ylabel('Water temperature (ºC)')
plt.title('Posterior predictive error of simulations during 2015 and validation')
plt.legend(['Predictions', '2.5% interval of pred.', '97.5% interval of pred',
            'Observations'])
plt.savefig('fig6c.png')
plt.close()

# Predictive error (only 1st and 15th day in each month)
t_vec = [np.datetime64('2015-{:02d}-01'.format(i)) for i in np.arange(1, 13)] +\
    [np.datetime64('2015-{:02d}-15'.format(i)) for i in np.arange(1, 13)]
t_vec.sort()
res = la.pst.res
pred_names = ['temp_' + str(d).replace('-', '') for d in t_vec]
pred_names.sort()
twest = res.loc[pred_names, 'modelled']
errvar_res = la.get_errvar_dataframe(2)
post_var = errvar_res['first'] + errvar_res['second'] + errvar_res['third']
post_sd = np.sqrt(post_var.values[0])

plt.figure()
plt.plot(t_vec, twest, 'k-')
plt.plot(t_vec, twest+2*post_sd, 'k--')
plt.plot(t_vec, twest-2*post_sd, 'k--')
plt.xlabel('Date')
plt.ylabel('Water temperature (ºC)')
plt.title('Posterior predictive error of simulations during 2015')
plt.legend(['Predictions', '2.5% interval of pred.', '97.5% interval of pred.'])
plt.savefig('fig6d.png')
plt.close()
