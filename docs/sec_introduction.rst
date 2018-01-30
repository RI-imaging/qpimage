============
Introduction
============

.. automodule:: qpimage

.. toctree::
  :maxdepth: 2


The Problem
===========
Quantitative phase imaging (QPI) is a fundamental imaging technique
that visualizes the retardation of electromagnetic radiation as
it passes through an object. The parameter that governs this
retardation is called
`refractive index <https://en.wikipedia.org/wiki/Refractive_index>`_.
In biological imaging, QPI is an important tool to measure the
dry mass or the refractive index (related to mass density 
:cite:`Barer1952` :cite:`davieswilkins1952`) of single cells and tissues,
which enables a profound characterization of the investigated samples.   


Why qpimage?
============
In the `Guck group <https://gucklab.com/>`_, we make heavy use of QPI
and thus require a reliable and well-documented software
library that, independent of the particular QPI setup used, allows us
to address QPI-related research questions.
Qpimage attempts to unify QPI analysis by providing
a unique and user-friendly API for working with QPI data,
including the choice of input data (complex field, phase with
amplitude or intensity, hologram),
memory-efficient and fast storage of large data sets 
(using `HDF5 <https://en.wikipedia.org/wiki/Hierarchical_Data_Format>`_,
phase and amplitude data are stored separately),
or robust and extendable background correction techniques (tilt and
second order polynomial fits, binary mask).
The main reason for the development of qpimage is our QPI analysis software
`DryMass <https://drymass.readthedocs.io/en/stable/>`_.


Citing qpimage
==============
If you are using qpimage in a scientific publication, please
cite it with:

::

  (...) using qpimage version X.X.X (available at
  https://pypi.python.org/pypi/qpimage).

or in a bibliography

::
  
  Paul Müller (2017), qpimage version X.X.X: Phase image analysis
  [Software]. Available at https://pypi.python.org/pypi/qpimage.

and replace ``X.X.X`` with the version of qpimage that you used.


Furthermore, several ideas implemented in qpimage have been described
and published in scientific journals:

- Phase retrieval from holographic images with a gaussian
  filter is implemented according to :cite:`Schuermann2015`.

- Phase background image correction with a tilt fitted to a
  border of the image data was used in :cite:`Schuermann2015` and
  :cite:`Schuermann2016`.

- Phase background image correction with a polynomial fitted to
  known background regions was introduced for DHM in :cite:`Colomb2006`
  (in this reference the phase correction is applied to the hologram
  data before field reconstruction).

- Intensity background correction by dividing by a reference
  intensity image for tomographic imaging was used in 
  :cite:`Schuermann2017`.
