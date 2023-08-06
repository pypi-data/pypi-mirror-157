
#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages

PACKAGE = "cryptography3"

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="cryptography3",
    version=__import__(PACKAGE).__version__,
    author="duenldnkjdhlkq",
    author_email="duenldnkjdhlkq@foxmail.com",
    description="cryptography3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/MemoryD/mxgames",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)