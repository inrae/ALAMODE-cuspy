"""TEST # 5: Iterative Ensemble Smoother.

Apply an iterative ensemble smoother to OKP simulations.
"""
import os
import time
from shutil import rmtree, copytree

from cuspy import ies


# Configure test
parallel = False  # True, False (parallelize calculations)

# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
test0_folder = os.path.join(folder0, "test0")
folder = os.path.join(folder0, 'test5')
if os.path.isdir(folder):
    rmtree(folder)
copytree(test0_folder, folder)  # Copy data from test0_folder to folder
os.chdir(folder)

# Carry IES
t0 = time.time()
pst = ies(pst_file0=os.path.join(folder, 'test0.pst'),
          pst_file1=os.path.join(folder, 'test5.pst'),
          pestpp_folder=pestpp_folder,
          parallel=parallel, n_reals=50, control_data={'noptmax': 10})
t1 = time.time()

print('IES took %.1f s' % (t1 - t0))
