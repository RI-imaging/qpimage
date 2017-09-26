#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import dirname, realpath, exists
from setuptools import setup
import sys


author = u"Paul Müller"
authors = [author]
name = 'qpimage'
description = 'Python3 library for handling quantitative phase imaging data'
year = "2017"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
from _version import version

if __name__ == "__main__":
    setup(
        name=name,
        author=author,
        author_email='paul.mueller@biotec.tu-dresden.de',
        url='http://RI-imaging.github.io/qpimage/',
        version=version,
        packages=[name],
        package_dir={name: name},
        license="MIT",
        description=description,
        long_description=open('README.rst').read() if exists('README.rst') else '',
        install_requires=["numpy",
                          "scikit-image",
                          "scipy"],
        setup_requires=['pytest-runner'],
        tests_require=["pytest"],
        python_requires='>=3.0',
        keywords=["quantitative phase imaging",
                  "digital holographic microscopy",
                  ],
        classifiers= [
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3 :: Only',
            'Intended Audience :: Science/Research'
                     ],
        platforms=['ALL'],
        )
