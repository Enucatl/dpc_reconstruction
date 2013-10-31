#pylint: disable=C0111

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from version import get_git_version

setup(
    name = "dpc_reconstruction",
    version = get_git_version(),
    packages = find_packages(exclude='test'),
    scripts = [
        "bin/dpc_make_hdf5.py",
        ],

    install_requires = [
        'h5py',
        'numpy',
        'pypes',
        'pypesvds',
        ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
    
    entry_points = """
        [pypesvds.plugins] 
        dpc_reconstruction = dpc_reconstruction.template:Template

        [distutils.setup_keywords]
        paster_plugins = setuptools.dist:assert_string_list
  
        [egg_info.writers]
        paster_plugins.txt = setuptools.command.egg_info:write_arg
    """,


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
