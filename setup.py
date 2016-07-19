# pylint: disable=all

from setuptools import setup, find_packages
from subprocess import check_output


setup(
    name="dpc_reconstruction",
    version="v4.0.0",
    packages=find_packages(exclude='test'),
    install_requires=[
        'numpy',
        'h5py',
        'click',
        'tensorflow',
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
    entry_points="""
    [console_scripts]
    flats_every = bin.flats_every:main
    visibility = bin.visibility:main
    """
    # could also include long_description, download_url, classifiers, etc.
)
