from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'A module to help you make a blockchain'
LONG_DESCRIPTION = 'This package helps make a blockchain with less than 10 lines of code!'

# Setting up
setup(
    name="blockchainpack",
    version=VERSION,
    author="Advaith S",
    author_email="<popular9adu@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'blockchain', 'python3', 'cryptocurrency'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)