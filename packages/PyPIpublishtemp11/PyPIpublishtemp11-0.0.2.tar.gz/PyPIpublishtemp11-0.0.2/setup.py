#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "PyPIpublishtemp11",
    version = "0.0.2",
    keywords = ["a test script of PyPI"],
    description = "a test script of PyPI.",
    long_description = "a test script of PyPI.",

    url = "https://github.com/XinQ2020/Pypi-test",
    author = "XinQ020",
    author_email = "1969848456@qq.com",
    license= "MIT license ",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [],

)