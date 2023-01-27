"""TEST # 7: Test the function :func:`input_output.process_swp_out()`.

Check whether the partial averages calculation functionality of the
function :func:`input_output.process_swp_out()` works correctly.
Test 4 should have been previously run in order to create the
:file:`sweep_out.csv` file.
"""
import os.path
from shutil import rmtree

from cuspy import process_sweep_out


# Set folders
whereami = os.path.dirname(os.path.realpath(__file__))
if __file__ == '<input>':
    folder0 = os.path.join(whereami, 'tests')
else:
    folder0 = whereami

# configure test
fname_in = os.path.join(folder0, "test4", "sweep_out.csv")
folder_out = os.path.join(folder0, "test7")
if os.path.isdir(folder_out):
    rmtree(folder_out)
os.mkdir(folder_out)

process_sweep_out(fname_in=fname_in, folder_out=folder_out,
                  var_names=['tepi', 'thyp'],
                  ptl_avg={'tepi': ['tepi', 'thyp'],
                           'thyp': ['tepi', 'thyp']})
