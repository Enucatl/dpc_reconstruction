# pylint: disable=all

from setuptools import setup, find_packages
from version import get_git_version
from subprocess import check_output


setup(
    name="dpc_reconstruction",
    version=get_git_version(),
    packages=find_packages(exclude='test'),
    scripts=[
        "bin/fliccd2hdf5.py",
        "bin/shadobox2hdf5.py",
        "bin/visibility.py",
        "bin/reconstruction.py",
        "bin/flats_every.py",
    ],

    install_requires=[
        'numpy',
        'h5py',
        'matplotlib',
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
