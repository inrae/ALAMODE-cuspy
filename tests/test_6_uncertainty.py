"""TEST 6: Make uncertainty calculations

Calibrate the OKP model with Tikhonov regularization using the cuspy
package. Then, make uncertainty calculations.
"""
import os
from shutil import copytree, rmtree
import time

from cuspy import calibration, linear_uncertainty

# Set uncertainty analysis
analysis = 'prior'  # 'prior', 'schur', 'err_var'

# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
test0_folder = os.path.join(folder0, "test0")
folder = os.path.join(folder0, 'test6')
if os.path.isdir(folder):
    rmtree(folder)
copytree(test0_folder, folder)  # Copy data from test0_folder to folder
os.chdir(folder)

# Calibrate model (with GLM method)
calibration(method='glm', reg=True,
            pst_file0=os.path.join(folder, 'test0.pst'),
            pst_file1=os.path.join(folder, 'test6.pst'),
            pestpp_folder=pestpp_folder, parallel=False,
            control_data={'noptmax': 10})


# Uncertainty analysis
t0 = time.time()
la = linear_uncertainty(analysis=analysis, pst_file0='test6.pst',
                        pst_file1='test6b.pst', pestpp_folder=pestpp_folder)
t1 = time.time()
print(t1-t0)
