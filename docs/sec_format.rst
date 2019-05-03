================
HDF5 file format
================

The data of a :class:`qpimage.QPImage` or :class:`qpimage.QPSeries` can be
stored on disk, using the ``h5file`` parameter upon class instantiation.
This section describes the scheme used to store the data using the
`HDF5 file format <https://en.wikipedia.org/wiki/Hierarchical_Data_Format#HDF5>`_.

QPImage
=======
The following graph visualized the HDF5 file structure of a QPImage instance:

.. graphviz::

     graph example {
         graph [rankdir=LR];
         QPImage [shape="folder", label="/"];
         amplitude [shape="folder"];
         phase [shape="folder"];
         raw [shape="component"];
         bg_data [shape="folder"];
         data [shape="component"];
         fit [shape="component"];
         "..." [shape="box"];
         "estimate_bg_from_mask" [shape="component"];
         QPImage -- amplitude;
         QPImage -- phase;
         amplitude -- raw;
         amplitude -- bg_data;
         bg_data -- data;
         bg_data -- fit;
         bg_data -- "estimate_bg_from_mask";
         phase -- "...";
     }


Attributes
----------
These attributes of the root group (/) describe physical parameters of the data:

.. qpimage_meta_table:: data


These other attributes may be used by e.g. data simulators such as
:ref:`qpsphere <qpsphere:index>` or :ref:`cellsino <cellsino:index>`:

.. qpimage_meta_table:: other


Groups
------
Both groups, *amplitude* and *phase*, do not hold attributes.
Each of the groups contain a dataset called *raw* (the raw image, by default
stored as 32bit floating point values) and a group called *bg_data* which
contains information about background correction. If background correction
was used, then the *bg_data* group may contain the following datasets:

- *data*: simple background image
- *fit*: fitted background image; has the additional attributes
  ``fit_offset``,  ``fit_profile``, and ``border_px``
  (see :func:`qpimage.core.QPImage.compute_bg` for possible values)
- *estimate_bg_from_mask*: binary mask image that defines regions in
  *raw* that resemble background data; used for background fitting 

All of these datasets have the same shape as *raw*. The *data* and *fit*
datasets form the background data that are internally removed from the *raw*
data when requesting the ``QPImage.amp`` or ``QPImage.pha`` properties.

QPSeries
========
The following graph visualized the HDF5 file structure of a QPSeries instance
(with a total of 48 QPImages):

.. graphviz::

     graph example {
         node [shape="folder"];
         graph [rankdir=LR, center=1];
         QPSeries [label="/"]
         qp1 [label="qpi_1"]
         qp2 [label="qpi_2"]
         a1 [shape="box", label=ampltitude];
         a2 [shape="box", label=phase];
         d0 [shape="box", label="..."];
         d1 [shape="box", label="..."];
         d2 [shape="box", label="..."];
         d3 [shape="box", label="..."];
         d4 [shape="box", label="..."];
         qp3 [label="qpi_47"]
         QPSeries -- qp1;
         qp1 -- a1;
         qp1 -- a2;
         a1 -- d0;
         a2 -- d1;
         QPSeries -- qp2;
         qp2 -- d2;
         QPSeries -- d4;
         QPSeries -- qp3;
         qp3 -- d3;
     }

Note that the name of each QPImage group always starts with "qpi\_" and that the
enumeration does not contain leading zeros. The root node (/) of a QPSeries
may have the *identifier* attribute.

