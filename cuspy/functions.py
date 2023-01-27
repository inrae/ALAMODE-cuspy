"""Useful functions.

The function in this module is used to launch the PEST++ executable.

This module contains the following function:

    * :func:`launch_pestpp`: launch PEST++ executable

"""
# Copyright 2020-2023 Segula Technologies - Office Français de la Biodiversité.
#
# This file is part of the Python package "cuspy".
#
# The package "cuspy" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The package "cuspy" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "cuspy".  If not, see <https://www.gnu.org/licenses/>.
import os
import subprocess

import pyemu


def launch_pestpp(pst_file, pestpp_folder, pestpp_cmd='pestpp-glm',
                  parallel=False):
    """Launch PEST++ executable.

    This function launches the requested PEST++ executable, either
    making calculations on line or in parallel. The PEST++ executables
    and uses are:

    * PESTPP-GLM: highly parameterized inversion and global
      optimization (i.e., parameter optimization, calibration).
    * PESTPP-SEN: global sensitivity analysis.
    * PESTPP-OPT: constrained optimization under uncertainty (White et
      al. 2018).
    * PESTPP-IES: interative ensemble smoothing (White 2018).
    * PESTPP-SWP: Monte Carlo simulations.

    For more details on the PEST++ executables, please see White et al.
    (2019).

    Args:
        pst_file: path of pest control file (.pst).
        pestpp_folder: folder containing the PEST++ executables.
        pestpp_cmd: PEST++ executable. The PEST++ executables are:
            "pestpp-glm", "pestpp-sen", "pestpp-opt", "pestpp-ies" and
            "pestpp-swp".
        parallel: parallelize calculations.

    Returns:
        The output of the PEST++ command is shown on screen. In
        addition, the `pestpp_cmd` output files are written in the
        folder containing the `pst_file`.

    References:
        * White, J.T. (2018) A model-independent iterative ensemble
          smoother for efficient history matchingh and uncertainty
          quantification in very high dimensions. *Environmental
          Modelling and Software* 109,  191-201.
        * White, J.T.; Fienen, M.N.; Barlow, P.M.; Welter, D.E. (2018)
          A tool for efficient, model-independent management
          optimization under uncertainty. *Environmental Modelling and
          Software* 100, 2013-221.
        * White, J.; Welter, D.; Doherty, J. (2019) *PEST++ Version
          4.2.16*. PEST++ Development Team. 175 p.
    """
    if parallel:
        # Set folders and paths
        folder = os.path.dirname(pst_file)
        master_dir = os.path.join(folder, 'master')
        exe_path = os.path.join(pestpp_folder, pestpp_cmd)
        exe_rel_path = os.path.relpath(exe_path, master_dir)
        pst_rel_path = os.path.basename(pst_file)
        worker_root = os.path.dirname(master_dir)
        # Run PEST++ command
        pyemu.helpers.start_workers(worker_dir=folder,
                                    exe_rel_path=exe_rel_path,
                                    pst_rel_path=pst_rel_path,
                                    worker_root=worker_root,
                                    master_dir=master_dir)
    else:
        # Run PEST++ command
        subprocess.run([os.path.join(pestpp_folder, pestpp_cmd),
                        pst_file])
    return
