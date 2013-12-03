# DPC Reconstruction

## Requirements

[pyenv](https://github.com/yyuu/pyenv) and [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv) to easily manage different python versions.

[Stackless Python](http://www.stackless.com/) 2.7.2

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

## Packages for scientific linux 6

    :::bash
    su -c 'yum install {libpng,freetype,readline,bzip2,sqlite,hdf5}-devel'

## Install the requirements

    :::bash
    #install pyenv
    cd
    git clone git://github.com/yyuu/pyenv.git .pyenv
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/shims:$PATH"' >> ~/.bashrc
    source ~/.bashrc

    #install pyenv-virtualenv
    git clone git://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

    #install stackless python 2.7.2
    pyenv install stackless-2.7.2
    pyenv rehash
    pyenv virtualenv stackless-2.7.2 stackless-python
    pyenv rehash

    #install the python style and syntax checkers
    pip install pep8
    pip install pylint
    pyenv rehash


## Install

    :::bash
    mkdir ~/bin; cd ~/bin
    pip install --upgrade setuptools
    pip install pytest
    pip install numpy
    pip install h5py
    pip install matplotlib
    pyenv rehash
    git clone git@bitbucket.org:psitomcat/dpc_reconstruction.git
    cd dpc_reconstruction

    #install pypes
    git clone https://github.com/Enucatl/pypes.git ~/bin/pypes
    pushd ~/bin/pypes
    python bootstrap.py
    bin/buildout
    cd core
    python setup.py install
    cd ../ui
    pip install pylons
    pip install elementtree
    python setup.py install

    #come back to the dpc_reconstruction folder
    #and install the pipeline components
    popd
    make install

## Structure

A template for the pipeline components is available in the
`dpc_reconstruction/template.py` file.

The executable programs are in the `bin` folder. They are expected not to
print any output, as in the linux commandline tradition, when they run
successfully. Run them with the `--verbose` option to get more info on what
is actually going on.

## Code style

The repository is set up in a way that prevents commits
that do not pass both the [pylint](http://www.pylint.org/) and [pep8](https://pypi.python.org/pypi/pep8) checks.

Exceptions to these rules need to be discussed and added to the repository
beforehand.
