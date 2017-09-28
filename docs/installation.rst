Installing qpimage
==================

Qpimage is written in pure Python and only supports Python version 3.5
and higher. Qpimage depends on several other scientific Python packages,
including:

 - :py:mod:`numpy`,
 - :py:mod:`scipy`,
 - :py:class:`h5py.File` (caching),
 - :py:mod:`lmfit` (background estimation),
 - :mod:`nrefocus` (numerical focusing), and
 - :py:func:`scikit-image.restoration.unwrap_phase` (phase unwrapping).
    

To install imageio, use one of the following methods:
    
* from PyPI: ``pip install qpimage``
* from sources ``pip install .`` or ``python setup.py install``
