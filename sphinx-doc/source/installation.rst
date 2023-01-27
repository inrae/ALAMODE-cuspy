Installation
============

Requirements and dependencies
-----------------------------
You need Python 3.6 or later to run the :mod:`cuspy` package. You can have
multiple Python versions (2.x and 3.x) installed on the same system
without problems using, for example, virtual environments.

You may use ``pip`` to install the required packages.

.. note:: In Windows, to use ``pip`` to install the required packages, please verify
   that the path to ``pip``'s executable file has been added correctly to your
   environment variable ``PATH``. The address may vary depending on whether you install
   it for one or all users (e.g., :file:`%USERPROFILE%/AppData/roaming/Python/Python37/scripts`
   or :file:`C:/Users/MyUserName/AppData/Local/Programs/Python/Python37/Scripts`).

The application :mod:`cuspy` depends on the Python packages :mod:`numpy`, :mod:`pandas`
and :mod:`pyemu`. The package :mod:`pyemu` also depends on :mod:`matplotlib`
for plotting. Make sure they are installed before using :mod:`cuspy`.

In addition, :mod:`cuspy` relies on the use of the PEST++ executables.
PEST++ executables for Windows are available at https://github.com/usgs/pestpp/bin/win,
but you will need to compile them for Linux (see the instructions below,
`Compiling PEST++ executables`_).

If you do not have to compile the documentation, :mod:`sphinx` is not
necessary to use :mod:`cuspy`, since a precompiled pdf copy of the documentation is
included in the folder :file:`docs`.

If you need to compile the documentation from source (e.g., to modify it),
you will need the package :mod:`sphinx`. To install :mod:`sphinx` just make:

.. code:: shell

    pip install sphinx

The package :mod:`sphinx` works by default with reStructuredText documents. However,
it can also recognise Markdown by installing the Markdown parser :mod:`recommonmark`.

.. code:: shell

    pip install --upgrade recommonmark

To create multilingual documentation, you will need the package :mod:`sphinx-intl`.
The installation process is as above:

.. code:: shell

    pip install sphinx-intl

To compile pdf documents (only in Linux), you will also need to have installed
latex and the Python package :mod:`latexmk`. To install latex, type:

.. code:: shell

    sudo apt-get install texlive-full

And to install :mod:`latexmk`, type:

.. code:: shell

    pip install latexmk.py

On Ubuntu you may use:

.. code:: shell

    sudo apt install latexmk

Cloning repositories
--------------------
You need to clone the :mod:`cuspy` package and :mod:`pestpp` source with git.
For this go to an appropriate directory (e.g., :file:`pathtoprojectsfolder`)
where to copy the project's code in a subfolder and clone the project.
For example, for :mod:`cuspy`:

.. code:: shell

    cd pathtoprojectsfolder
    git clone https://github.com/inrae/ALAMODE-cuspy

This command creates the :mod:`cuspy` repertory in the folder
:file:`pathtoprojectsfolder`.

To install the development branch of the project,
after cloning the :mod:`cuspy` package, change to the ``dev`` branch:

.. code:: shell

    cd cuspy
    git checkout dev

To clone the ``pestpp`` source, do:

.. code:: shell

    cd pathtoprojectsfolder
    git clone https://github.com/usgs/pestpp


Compiling PEST++ executables
----------------------------
If you work on Linux, you need to compile the PEST++ executables. For this
you will need to have ``gcc``, ``gfortran`` and the libraries ``lapack``
and ``blas`` installed. To install them you can use:

.. code:: shell

    sudo apt-get install gcc gfortran
    sudo apt-get install liblapack-dev libblas-dev


To compile the PEST++ executables, go to the :file:`pestpp/src` folder and do:

.. code:: shell

    make clean
    STATIC=no make install

The compiled executables can then be found in the folder :file:`pestpp/bin/linux`.

Installing :mod:`cuspy`
-----------------------
To install :mod:`cuspy`, go to the repertory created during the cloning of the
package :mod:`cuspy` (e.g., :file:`pathtorepertorycuspy`) and install
it using ``pip``:

.. code:: shell

    cd pathtorepertorycuspy
    pip install -U .

Compilation of the project documentation
----------------------------------------
The source files for the project user manual are stored in the folder
:file:`pathtorepertorycuspy/sphinx-doc/source`. Sphinx also extracts data from the
project modules docstrings.

Documentation in English
^^^^^^^^^^^^^^^^^^^^^^^^
To compile the user manual in English as html files
go to the folder :file:`pathtorepertorycuspy/sphinx-doc` and type:

.. code:: shell

    make html

The output html files are saved in the folder
:file:`pathtorepertorycuspy/sphinx-doc/build/html`.

You can also compile the user manual as a pdf file making:

.. code:: shell

    make latexpdf

The source documentation files are converted to latex and then to pdf. The
output latex and pdf files are saved in the folder
:file:`pathtorepertorycuspy/sphinx-doc/build/latex`.

Documentation in French
^^^^^^^^^^^^^^^^^^^^^^^
To compile the user manual in French as html files
go to the folder :file:`pathtorepertorycuspy/sphinx-doc` and type:

.. code:: shell

    sphinx-build -b html -aE -D language='fr' -c source/locale/fr source build_fr/html

The output html files are saved in the folder
:file:`pathtorepertorycuspy/sphinx-doc/build_fr/html`.

To compile the pdf documentation, type the following commands:

.. code:: shell

    sphinx-build -b latex -aE -D language='fr' -c source/locale/fr source build_fr/latex
    cd build_fr/latex
    make

The source documentation files are converted to latex and then to pdf. The
output latex and pdf files are saved in the folder
:file:`pathtorepertorycuspy/sphinx-doc/build_fr/latex`.
