from distutils.core import setup
from mitoinstaller import __version__
from setuptools import find_packages

print(find_packages(where='.', exclude='tests'))

setup(
    name='mitoinstaller',
    version=__version__,
    packages=find_packages(where='.', exclude='tests'),
    install_requires=['analytics-python', 'colorama', 'termcolor'],
    license='TODO',
    long_description='The mitoinstaller package allows you to install the mitosheet package in your local JupyterLab instance. It logs anonymous data about installation, including if it is successful or why it failed.',
)
