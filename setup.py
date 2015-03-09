# pylint: disable=all

from setuptools import setup, find_packages
from subprocess import check_output


setup(
    name="dpc_reconstruction",
    version="v3.0.0",
    packages=find_packages(exclude='test'),
    scripts=[
        "bin/mythen2hdf5.py",
        "bin/pilatus2hdf5.py",
        "bin/fliccd2hdf5.py",
        "bin/shadobox2hdf5.py",
        "bin/visibility.py",
        "bin/reconstruction.py",
        "bin/flats_every.py",
    ],

    install_requires=[
        'numpy',
        'h5py',
        'pypes',
    ],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author="TOMCAT DPC group",
    author_email="",
    description="Analyse phase stepping curves",
    license="GNU GPL 3",
    keywords="",
    # project home page, if any
    url="https://bitbucket.org/psitomcat/dpc_reconstruction",
    # could also include long_description, download_url, classifiers, etc.
)
