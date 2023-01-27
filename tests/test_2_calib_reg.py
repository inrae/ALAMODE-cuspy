"""TEST 2: Calibrate function (with regularization)

Calibrate the OKP model with Tikhonov regularization using the cuspy
package. In contrast to test_1, only the GLM method is tested here.
"""
import os
from shutil import copytree, rmtree
import time

from cuspy import calibration

# Configure calibration
parallel = True  # True or False (parallelize calculations)

# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
test0_folder = os.path.join(folder0, "test0")
folder = os.path.join(folder0, 'test2')
if os.path.isdir(folder):
    rmtree(folder)
copytree(test0_folder, folder)  # Copy data from test0_folder to folder
os.chdir(folder)

# Calibrate model (with GLM method)
t0 = time.time()
pst = calibration(method='glm', reg=True,
                  pst_file0=os.path.join(folder, 'test0.pst'),
                  pst_file1=os.path.join(folder, 'test2.pst'),
                  pestpp_folder=pestpp_folder, parallel=parallel,
                  control_data={'noptmax': 10})
t1 = time.time()
print(t1-t0)

print('Calibration took %.1f s' % (t1 - t0))
