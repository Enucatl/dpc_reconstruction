# DPC Reconstruction

## Requirements

[pyenv](https://github.com/yyuu/pyenv) and [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv) to easily manage different python versions. We are using [Stackless Python](http://www.stackless.com/)

[GIT](http://git-scm.com/ "GIT homepage") version control system ≥ 1.7

[Python Setuptools](https://pypi.python.org/pypi/setuptools) for
installing the python scripts

[Numpy](http://www.numpy.org/) for the calculations (very similar to
matlab!)

[HDF5](http://www.hdfgroup.org/HDF5/) for the image storage

[pypes](https://github.com/Enucatl/pypes) for the pipeline

## Report Bugs & Request Features

please report any bug or feature request using the [issues webpage](https://bitbucket.org/psitomcat/dpc_reconstruction/issues?status=new&status=open).

## Download

    :::bash
    git clone git@bitbucket.org:psitomcat/dpc_reconstruction.git

## Install

Starting from the installation of stackless python

    :::bash
    git clone https://Enucatl@bitbucket.org/psitomcat/dpc_reconstruction.git
    cd dpc_reconstruction

    #install stackless python
    pyenv virtualenv stackless-2.7.2 stackless-python

    #install pypes
    git clone https://github.com/Enucatl/pypes.git ~/bin/pypes
    pushd ~/bin/pypes
    python bootstrap.py
    bin/buildout
    cd core
    pip install --upgrade setuptools
    python setup.py install
    cd ../ui
    pip install pylons
    pip install elementtree
    python setup.py install

    #come back to the dpc_reconstruction folder
    #and install the pipeline components
    popd
    pip install numpy
    pip install h5py
    pip install matplotlib
    python setup.py install
    python setup.py bdist_egg --dist-dir ~/bin/pypes/plugins/

## Structure

A template for the pipeline components is available in the TemplateComponent
file.

## Code style

Please follow the Python Enhancement Proposal n. 8
[PEP8](http://www.python.org/dev/peps/pep-0008/) for all the python code.
