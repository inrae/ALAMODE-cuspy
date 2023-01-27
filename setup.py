# Copyright 2020-2023 Segula Technologies - Office Français de la Biodiversité.
from setuptools import setup, find_packages

# read version
exec(open('cuspy/_version.py').read())

# import long description data
with open('README.md', 'r') as f:
    long_description = f.read()

# configure setup
setup(
    name='cuspy',
    version=__version__,
    packages=find_packages(),
    author=['Jordi Prats-Rodríguez', 'Pierre-Alain Danis'],
    author_email=['jprats@segula.es', 'pierre-alain.danis@ofb.gouv.fr'],
    description='Calibration, Uncertainty and Sensitivity analyses in PYthon',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.irstea.fr/alamode/cuspy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or ' +
        'later (GPLv3+)'],
    python_requires='>=3.5',
    install_requires=['numpy', 'pandas', 'pyemu==1.0'],
    entry_points={
        'console_scripts': []}
)
