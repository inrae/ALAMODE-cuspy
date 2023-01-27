import os

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Read data
folder = '/nfs/alamode/Donnees_test/NAU48/'
meteo = pd.read_csv(os.path.join(folder, 'meteo.csv'), parse_dates=[0])

tw = pd.read_csv(os.path.join(folder, 'model_fld_tempSAT_b.wtr'), sep=';',
                 parse_dates=[0])
ind = np.in1d(meteo['time'], tw['time'])
ind2 = tw['time'] <= np.datetime64('2015-12-31')

plt.figure()
plt.plot(meteo['AirTemp'][ind], tw['temp0.000'][ind2], '*')
plt.plot([0, 25], [0, 25], 'k--')
plt.xlim([0, 25])
plt.ylim([0, 25])
plt.xlabel('Air temperature (ºC)')
plt.ylabel('Water temperature (ºC)')
plt.savefig('fig1.png')
