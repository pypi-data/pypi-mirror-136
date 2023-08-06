import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "convstruct",
    version = "1.1.0",
    license = "Apache Licence 2.0",
    description = "NAS + RL",
    long_description = read('README.md'),
    author = "convstruct",
    author_email = "hello@convstruct.org",
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
)
