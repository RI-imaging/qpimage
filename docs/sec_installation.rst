Installing qpimage
==================

Qpimage is written in pure Python and supports Python version 3.6
and higher. Qpimage depends on several other scientific Python packages,
including:

 - `numpy <https://docs.scipy.org/doc/numpy/>`_,
 - `scipy <https://docs.scipy.org/doc/scipy/reference/>`_,
 - `h5py <https://docs.h5py.org/en/stable>`_ (caching),
 - `lmfit <https://lmfit.github.io/lmfit-py/>`_ (background estimation),
 - `nrefocus <https://nrefocus.readthedocs.io/>`_ (numerical focusing), and
 - `scikit-image <http://scikit-image.org/>`_ (phase unwrapping using :py:func:`skimage.restoration.unwrap_phase`).
    

To install qpimage, use one of the following methods
(package dependencies will be installed automatically):
    
* from `PyPI <https://pypi.python.org/pypi/qpimage>`_:
    ``pip install qpimage``
* from `sources <https://github.com/RI-imaging/qpimage>`_:
    ``pip install -e .`` or
