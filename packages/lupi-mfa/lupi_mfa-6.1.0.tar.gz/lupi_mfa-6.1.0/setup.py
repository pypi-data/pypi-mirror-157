import os
from setuptools import setup

PACKAGE_NAME = 'lupi_mfa'

def read_package_variable(key):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, '__init__.py')
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ')
            if parts and parts[0] == key:
                return parts[-1].strip("'")
    assert False, "'{0}' not found in '{1}'".format(key, module_path)

setup(
    name=PACKAGE_NAME,
    version=read_package_variable('__version__'),
    description='Perspecta Labs LupiMFA primitive',
    maintainer_email='plin@perspectalabs.com',
    maintainer='Peter Lin',
    author=read_package_variable('__author__'),
    packages=['lupi_mfa'],
    install_requires=[
        'd3m',
        'scikit-learn',
        'pandas',
        'numpy',
    ],
    url='https://gitlab.com/datadrivendiscovery/contrib/lupi_mfa',
    entry_points = {
        'd3m.primitives': [
            'data_preprocessing.lupi_mfa.lupi_mfa.LupiMFA = lupi_mfa.lupi_mfa:LupiMFA'
        ],
    },
)
