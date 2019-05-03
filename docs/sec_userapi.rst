.. _userapi:

========
User API
========
The qpimage API is built upon the hdf5 file format using
`h5py <http://h5py.readthedocs.io/>`_. That means that each instance of
:py:class:`qpimage.QPImage <qpimage.core.QPImage>` generates an hdf5 file,
either on disk or in memory, depending on the preferences of the user. This
approach has the advantage that phase and amplitude data can be cached on disk,
including all parameters that were used for background correction, which
allows to transparently recapture any steps that were performed on a
specific data set at a later time point.

Basic usage
-----------
A typical use case of qpimage is

.. code-block:: python

   qpi = qpimage.QPImage(data=phase_ndarray, which_data="phase")
   # perform phase-tilt background correction
   qpi.compute_bg(which_data="phase",  # correct phase image
                  fit_offset="fit",  # use bg offset from tilt fit
                  fit_profile="tilt",  # perform 2D tilt fit
                  border_px=5,  # use 5 px border around image
   				  )
   # save the background-corrected phase to a text file
   numpy.savetxt("out.txt", qpi.pha)

which creates an instance of `QPImage` containing otherwise experimentally
obtained phase data, performs a phase-tilt background correction and then
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
                      fit_profile="tilt",
                      border_px=5,
                      )

where all data is stored in ``/path/to/file.h5``. This will create an hdf5
file on disk that, at a later time point, can be used to create an instance
of `QPImage`:

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
  - the parameters for reproducing the result of
    :py:func:`qpi.compute_bg <qpimage.core.QPImage.compute_bg>`

- all measurement specific meta data, given by the keyword argument
  ``meta_data``

Dealing with measurement series
-------------------------------
Qpimage also comes with a :py:class:`QPSeries <qpimage.series.QPSeries>`
class for handling multiple instances of QPImage in one hdf5 file. 
For instance, to combine two QPImages in one series file, one could
use:

.. code-block:: python

   paths = ["file_a.h5", "file_b.h5", "file_c.h5"]

   with qpimage.QPSeries(h5file="/path/to/series_file.h5", h5mode="w") as qps:
       for ii, pp in enumerate(paths):
           qpi = qpimage.QPImage(h5file="/path/to/file.h5", h5mode="r")
           qps.add_qpimage(qpi=qpi, identifier="my_name_{}".format(ii))

Note that the function `add_qpimage` accepts the optional keyword argument
"identifier" (overriding the identifier of the QPImage) which
can also be used for indexing later:

.. code-block:: python

   with qpimage.QPSeries(h5file="/path/to/series_file.h5", h5mode="r") as qps:
       # these two are equivalent
       qpi = qps[0]
       qpi = qps["my_name_0"]


Notes
-----
- Even though the hdf5 data is stored as gzip-compressed single precision
  floating point values, using qpimage hdf5 files
  may result in file sizes that are considerably
  larger compared to when only the output of e.g. ``qpi.pha`` is stored
  using e.g. :py:func:`numpy.save`.

- Units in qpimage follow the international system of units (SI).

- :py:class:`qpimage.QPSeries <qpimage.series.QPSeries>` provides a convenient way to manage multiple
  :py:class:`qpimage.QPImage <qpimage.core.QPImage>`, optionally storing them in a single hdf5 file.
