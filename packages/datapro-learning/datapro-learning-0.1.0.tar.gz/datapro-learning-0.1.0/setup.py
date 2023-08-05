from gettext import install
from setuptools import setup, find_packages

from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='datapro-learning',
    version="0.1.0",
    description="""learning common data structure""",
    long_description_content_type="text/markdown",
    long_description="""The task is learning the common structure of data. The DataPro algorithm is the algorithm that finds statistically significant patterns in a set of token sequences.
This repository is Implemented from the paper "Learning the Common Structure of Data" by Kristina Lerman and Steven Minton.""",
    url="https://github.com/NonKhuna/DataPro-Algorithm",
    author="Khunanon Rattanagoses",
    packages=["datapro"],
    include_package_data=True,
    install_requires=['pandas','numpy','pythainlp','scipy','openpyxl'],
)