# DPC Reconstruction

## Requirements

[pyenv](https://github.com/yyuu/pyenv) and [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv) to easily manage different python versions.

[GIT](http://git-scm.com/ "GIT homepage") version control system ≥ 1.7

[HDF5](http://www.hdfgroup.org/HDF5/) for the image storage

[tensorflow](https://www.tensorflow.org/) for the pipeline

## Report Bugs & Request Features

please report any bug or feature request using the [issues webpage]().

## Download

    git clone git@github.com:Enucatl/dpc_reconstruction.git

## Packages for scientific linux 6

    su -c 'yum install {libpng,freetype,readline,bzip2,sqlite,hdf5}-devel'

## Install the requirements

    Check out the tensorflow page to install tensorflow.

    #install pyenv
    cd
    curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

    #install python
    pyenv install $(cat .python-version)

    #install the python style and syntax checkers
    pip install pep8
    pip install pylint


## Install

    mkdir ~/bin; cd ~/bin
    pip install --upgrade setuptools
    pip install numpy
    pip install h5py
    make
    make install
    pyenv rehash

## Code style

The repository is set up in a way that prevents commits
that do not pass the [pep8](https://pypi.python.org/pypi/pep8) checks.

Exceptions to these rules need to be discussed and added to the repository
beforehand.
