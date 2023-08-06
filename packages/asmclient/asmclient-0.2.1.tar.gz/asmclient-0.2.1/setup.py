#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='asmclient',
    version='0.2.1',
    description='yxt bdai asmclient utility package',
    long_description=readme,
    author='luoyw',
    author_email='luoyw@yxt.com',
    url='http://172.17.128.21:9000/svn/bigdata/trunk/asm_authorization',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
