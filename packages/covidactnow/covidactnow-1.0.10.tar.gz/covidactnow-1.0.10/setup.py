from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.10'
DESCRIPTION = 'A wrapper allowing users to get specific state-based COVID information from the Covid Act Now database.'

def getReadMe():
    with open('README.md', 'r') as f:
        return f.read()

# Setting up
setup(
    name="covidactnow",
    version=VERSION,
    author="Prerit Das",
    author_email="<preritdas@gmail.com>",
    description=DESCRIPTION,
    long_description = getReadMe(),
    long_description_content_type = "text/markdown",
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'covid', 'rest', 'information', 'wrapper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
