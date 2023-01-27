"""TEST # 4: Make Monte Carlo simulations.

Make Monte Carlo simulations of the OKP model. Based on the results of
Test 1 (test_1_calib_overdet.py run with method='glm' and
parallel=False).
"""
import os
import time
from shutil import rmtree, copytree, copyfile

from cuspy import monte_carlo


# Configure test
method = 'prior'  # 'prior', 'post' (use prior or post. parameter dist.)
parallel = False  # True, False (parallelize calculations)

# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

pestpp_folder = os.path.expanduser("~/PycharmProjects/pestpp/bin/linux")
test0_folder = os.path.join(folder0, "test0")
folder = os.path.join(folder0, 'test4')
if os.path.isdir(folder):
    rmtree(folder)
copytree(test0_folder, folder)  # Copy data from test0_folder to folder
for f in ['test1.pst', 'test1.post.cov']:
    copyfile(os.path.join(folder0, 'test1', f),
             os.path.join(folder0, 'test4', f))
os.chdir(folder)

# Monte Carlo
# -----------
# Posterior uncertainty
t0 = time.time()
monte_carlo(pst_file0=os.path.join(folder, 'test1.pst'),
            pst_file1=os.path.join(folder, 'test4.pst'),
            dist_type=method, distribution='uniform', n_samples=50,
            pestpp_folder=pestpp_folder,
            csv_in=os.path.join(folder, 'sweep_in.csv'), parallel=parallel,
            process_swp_out=True)
t1 = time.time()

print('Monte Carlo took %.1f s' % (t1 - t0))
