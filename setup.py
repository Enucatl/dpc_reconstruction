#pylint: disable=C0111

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from version import get_git_version
from subprocess import check_output

def get_entry_points():
    """Get the names of all the classes inheriting from
    pypes.component.Component with some recursive grep magic.

    This is useful for installing the python egg for pypesvds so that the
    components can be used with the gui server.

    """
    command = r'''grep -rI "class \(.*\)(pypes.component.Component):" dpc_reconstruction | sed 's/.py:class /:/' | sed 's:/:.:g' | sed 's/(pypes.component.Component)://' | sed 's/\(.*\):\(.*\)/\2 = \1:\2/' '''
    result = check_output(command, shell=True)
    print(result)
    ini_config = '''
        [pypesvds.plugins] 
{0}
        [distutils.setup_keywords]
        paster_plugins = setuptools.dist:assert_string_list
  
        [egg_info.writers]
        paster_plugins.txt = setuptools.command.egg_info:write_arg
    '''.format(result)
    print(ini_config)
    return ini_config


setup(
    name = "dpc_reconstruction",
    version = get_git_version(),
    packages = find_packages(exclude='test'),
    scripts = [
        "bin/fliccd2hdf5.py",
        "bin/shadobox2hdf5.py",
        "bin/visibility.py",
        "bin/reconstruction.py",
        ],

    install_requires = [
        'numpy',
        'h5py',
        'matplotlib',
        'pypes',
        'pypesvds',
        ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
    
    entry_points = get_entry_points(), 

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
