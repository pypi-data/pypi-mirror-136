#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import os

version = "0.1.0.8"
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

setuptools.setup(
    name="hhycommon",
    version=version,
    author="lichanghong",
    author_email="1211054926@qq.com",
    description="加密等专用模块.",
    long_description=README,
    license='BSD License',
    long_description_content_type="text/markdown",
    url="https://hehuoya.com",
    install_requires=[
        'Crypto'
    ],
    packages=setuptools.find_packages(exclude=("hhycommon")),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    )

)