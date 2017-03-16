#!/usr/bin/env python
"""Setup script for GWsetp."""
import sys
import os

from glob import glob
from setuptools import find_packages

# changing Python version requirements.
if sys.version[0:3] < '2.7':
    sys.stderr.write("ERROR: GWplotting requires Python Version 2.7 or above. Exiting.")
    sys.exit(1)


def file_doesnt_end_with(test, endings):
    """
    A little utility we'll need below, since glob() does NOT allow you to do exclusion on multiple endings!

    Return true if test is a file and its name does NOT end with any
    of the strings listed in endings.
    """
    if not os.path.isfile(test):
        return False
    for e in endings:
        if test.endswith(e):
            return False
    return True

#---------------------------------------------------------------------------
# Basic project information
#---------------------------------------------------------------------------


def find_package_data():
    """Find pseudo_dojo's package_data."""
    package_data = {}
    return package_data


def find_scripts():
    """Find pseudo_dojo scripts."""
    scripts = []
    #
    # All python files in abipy/scripts
    pyfiles = glob(os.path.join('GWplotting', 'scripts', "*.py") )
    scripts.extend(pyfiles)
    return scripts


def cleanup():
    """Clean up the junk left around by the build process."""
    if "develop" not in sys.argv:
        import shutil
        try:
            shutil.rmtree('pseudo_dojo.egg-info')
        except:
            try:
                os.unlink('pseudo_dojo.egg-info')
            except:
                pass


# List of external packages we rely on.
# Note setup install will download them from Pypi if they are not available.
install_requires = [
    #"periodictable",
    #"numpy>=1.5",
    #"scipy>=0.10",
    "pymongo"
    "matplotlib>=1.1",
    "pymatgen>=2.9.0",
]

#---------------------------------------------------------------------------
# Find all the packages, package data, and data_files
#---------------------------------------------------------------------------

# Get the set of packages to be included.
my_packages = find_packages(exclude=())

my_scripts = find_scripts()

my_package_data = find_package_data()

# Create a dict with the basic information
# This dict is eventually passed to setup after additional keys are added.
setup_args = dict(name="GWplotting",
                  version="version",
                  description="description",
                  long_description="long_description",
                  author="author",
                  author_email="author_email",
                  #url=url,
                  #download_url=download_url,
                  license="license",
                  platforms="platforms",
                  keywords="keywords",
                  install_requires=install_requires,
                  packages=my_packages,
                  package_data=my_package_data,
                  scripts=my_scripts,
                  )


if __name__ == "__main__":
    from setuptools import setup
    setup(**setup_args)
    cleanup()
