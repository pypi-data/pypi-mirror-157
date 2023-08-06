#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2020 wesley wu
import os
from setuptools import setup, find_packages


def _requirements():
    with open('requirements.txt', 'r') as fd:
        return [name.strip() for name in fd.readlines()]


with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(
    name="redbird-sdk-python",
    version="1.0.1",
    author="wesley wu",
    author_email="jie1975.wu@gmail.com",
    maintainer="wesley wu",
    maintainer_email="jie1975.wu@gmail.com",
    url="https://github.com/weswu8/redbird-sdk-python",
    description="Intelligent algorithmic trading API",
    packages=find_packages(),
    long_description=open('README.md', 'r').read(),
    license='MIT License',
    install_requires=[
        'simplejson',
        'requests',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)