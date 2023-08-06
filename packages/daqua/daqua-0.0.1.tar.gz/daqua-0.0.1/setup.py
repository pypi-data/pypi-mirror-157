from pytz import VERSION
from setuptools import setup, find_packages
import codecs
import os

VERSION = "0.0.1"
DESCRIPTION = "To get the profiling report of a given excelFile"
LONG_DESCRIPTION = DESCRIPTION

setup(
    name="daqua",
    version=VERSION,
    author="Brainwind Engineering Team",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'pandas'],
    keywords=[],
    classifiers=[],
    
)