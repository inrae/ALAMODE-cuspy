"""TEST 1: Calibrate function (overdetermined case)

Calibrate the OKP model for the overdetermined case (nobs > npar) using
the cuspy package.

NB: depending on the type of calibration, running this script may take
quite a long time (especially for DE method with serial runs).
"""
import os
from shutil import copytree, rmtree
import time

from cuspy import calibration


# Configure calibration
method = 'glm'  # 'glm', 'de' (method used for calibration)
parallel = False  # True or False (parallelize calculations)

# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
test0_folder = os.path.join(folder0, "test0")
folder = os.path.join(folder0, 'test1')
if os.path.isdir(folder):
    rmtree(folder)
copytree(test0_folder, folder)  # Copy data from test0_folder to folder
os.chdir(folder)

# Calibrate model
t0 = time.time()
if method == 'glm':
    # method GLM
    pst = calibration(method='glm', reg=False,
                      pst_file0=os.path.join(folder, 'test0.pst'),
                      pst_file1=os.path.join(folder, 'test1.pst'),
                      pestpp_folder=pestpp_folder,
                      control_data={'noptmax': 10},
                      parallel=parallel)
elif method == 'de':
    # method DE
    pst = calibration(method='de', reg=False,
                      pst_file0=os.path.join(folder, 'test0.pst'),
                      pst_file1=os.path.join(folder, 'test1.pst'),
                      pestpp_folder=pestpp_folder,
                      pestpp_opts={'de_max_gen': 20}, parallel=parallel)
t1 = time.time()

print('Calibration took %.1f s' % (t1 - t0))
