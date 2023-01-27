"""TEST 3: Carry Global Sensitivity Analysis

Carry a GSA of the model OKP.

NB: GSA using Sobol's method can be lengthy (several minutes).
"""
import os
import time
from shutil import rmtree, copytree

from cuspy import gsa

# Configure test
method = 'morris'  # 'morris', 'sobol' (sensitivity method)
parallel = True  # True, False (parallelize calculations)

# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
test0_folder = os.path.join(folder0, "test0")
folder = os.path.join(folder0, 'test3')
if os.path.isdir(folder):
    rmtree(folder)
copytree(test0_folder, folder)  # Copy data from test0_folder to folder
os.chdir(folder)

# Carry sensitivity analysis
t0 = time.time()
if method == 'morris':
    # Morris's method
    gsa(method='morris',
        pst_file0=os.path.join(folder, 'test0.pst'),
        pst_file1=os.path.join(folder, 'test3_sen_morris.pst'),
        pestpp_folder=pestpp_folder, parallel=parallel)
elif method == 'sobol':
    # Sobol's method
    gsa(method='sobol',
        pst_file0=os.path.join(folder, 'test0.pst'),
        pst_file1=os.path.join(folder, 'test3_sen_sobol.pst'),
        pestpp_folder=pestpp_folder,
        pestpp_opts={'gsa_sobol_samples': 50}, parallel=parallel)
t1 = time.time()

print('Sensitivity calculations took %.1f s' % (t1 - t0))
# As an example calculation times were:
# morris, not parallel: 74.3 s
# morris, parallel (4 proc.): 53.0 s
# sobol, not parallel, 50 samples: 1027.7 s
# sobol, parallel (4 proc.), 50 samples: 441 s
