========
User API
========
The QPImage API is built upon the hdf5 file format using
`h5py <http://h5py.readthedocs.io/>`_. That means that each instance of
:py:class:`qpimage.QPImage` generates an hdf5 file, either on disk or
in memory, depending on the preferences of the user. This approach
has the advantage that phase and amplitude data can be cached on disk,
including all parameters that were used for background correction, which
allows to transparently recapture any steps that were performed on a
specific data set at a later time point.

Basic usage
-----------
A typical use case of qpimage is

.. code-block:: python

   qpi = qpimage.QPImage(data=phase_ndarray, which_data="phase")
   # perform phase-ramp background correction
   qpi.compute_bg(which_data="phase",  # correct phase image
                  fit_offset="fit",  # use bg offset from ramp fit
                  fit_profile="ramp",  # perform 2D ramp fit
                  border_px=5,  # use 5 px border around image
   				  )
   # save the background-corrected phase to a text file
   numpy.savetxt("out.txt", qpi.pha)

which creates an instance of `QPImage` containing otherwise experimentally
obtained phase data, performs a phase-ramp background correction and then
saves the corrected phase data to the text file "out.txt". In this case,
all data are stored in memory.

Storing QPImage data on disk
----------------------------
To cache the QPImage data on disk, use the ``with``
statement in combination with the ``h5file`` keyword argument

.. code-block:: python

   with qpimage.QPImage(data=phase_ndarray, which_data="phase", h5file="/path/to/file.h5") as qpi:
       qpi.compute_bg(which_data="phase",
                      fit_offset="fit",
                      fit_profile="ramp",
                      border_px=5,
                      )

where all data is stored in ``/path/to/file.h5``. This will create an hdf5
file on disk that, at a later time point, can be used to create an instance
of ``QPImage``:

.. code-block:: python

   # open previously cached data for reading
   qpi = qpimage.QPImage(h5file="/path/to/file.h5", h5mode="r")
   
   # or open cached data for writing (e.g. for changing the background)
   with qpimage.QPImage(h5file="/path/to/file.h5", h5mode="a") as qpi:
       # do something here

The default value of ``h5mode`` is "a", which means that data
will be overridden. In the hdf5 file, the following data is stored:

- all data for reproducing the background-corrected phase
  (``qpi.pha``) and amplitude (``qpi.amp``) (and thus field ``qpi.field``),
  including
  
  - the experimental phase data
  - the experimental background data
  - the parameters for reproducing the result of ``qpi.compute_bg``

- all measurement specific meta data, given by the keyword argument
  ``meta_data``

Notes
-----
- Using QPImage hdf5 files results in file sizes that are considerably
  larger compared to when only the output of e.g. ``qpi.pha`` is stored
  using e.g. :py:func:`numpy.save`.

- Units in qpimage follow the international system of units (SI).

- :py:class:`qpimage.QPSeries` provides a convenient way to manage multiple
  :py:class:`qpimage.QPImage`s, optionally storing them in a single hdf5 file.


QPImage
-------
.. autoclass:: qpimage.QPImage
    :members:

QPSeries
--------
.. autoclass:: qpimage.QPSeries
    :members:

Constants
---------
.. autodata:: qpimage.VALID_META_KEYS
