# DPC Reconstruction

## Requirements

[GIT](http://git-scm.com/ "GIT homepage") version control system ≥ 1.7

[Python Distribute](http://pythonhosted.org/distribute/index.html) for
installing the python scripts

[Numpy](http://www.numpy.org/) for the calculations (very similar to
matlab!)

[HDF5](http://www.hdfgroup.org/HDF5/) for the image storage

[pypes](http://www.ruffus.org.uk) for the pipeline


## Recommended

[pyenv](https://github.com/yyuu/pyenv) to easily manage different python
versions


## Report Bugs & Request Features

please report any bug or feature request using the [issues webpage](https://bitbucket.org/psitomcat/dpc_reconstruction/issues?status=new&status=open).


## Download

    :::bash
    git clone git@bitbucket.org:psitomcat/dpc_reconstruction.git


## Install

    :::bash
    python setup.py bdist_egg --dist-dir ~/bin/pypes/plugins/


## Structure

All the python code should be divided into meaningful packages and put
inside the `dpc_reconstruction` folder.


## Code style

Please follow the Python Enhancement Proposal n. 8
[PEP8](http://www.python.org/dev/peps/pep-0008/) for all the python code.
