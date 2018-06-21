from os.path import dirname, realpath, exists
from setuptools import setup, find_packages
import sys


author = u"Paul Müller"
authors = [author]
description = 'library for manipulating quantitative phase images'
name = 'qpimage'
year = "2017"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
from _version import version

setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/RI-imaging/qpimage',
    version=version,
    packages=find_packages(),
    package_dir={name: name},
    license="MIT",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=["h5py>=2.7.0",
                      "lmfit",
                      "nrefocus>=0.2.0",
                      "numpy>=1.9.0",
                      "scikit-image>=0.11.0",
                      "scipy>=0.18.0",
                      ],
    setup_requires=['pytest-runner'],
    tests_require=["pytest"],
    python_requires='>=3.6, <4',
    keywords=["digital holographic microscopy",
              "optics",
              "quantitative phase imaging",
              "refractive index",
              "scattering",
              ],
    classifiers= [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL'],
    )
