#pylint: disable=C0111

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from version import get_git_version

setup(
    name = "DPCReconstruction",
    version = get_git_version(),
    packages = find_packages(exclude='test'),
    scripts = [
        ],

    install_requires = [
        'h5py',
        'numpy',
        'scikit-image'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author = "TOMCAT DPC group",
    author_email = "",
    description = "Analyse phase stepping curves",
    license = "GNU GPL 3",
    keywords = "",
    # project home page, if any
    url = "https://bitbucket.org/psitomcat/dpc_reconstruction",
    # could also include long_description, download_url, classifiers, etc.
)
