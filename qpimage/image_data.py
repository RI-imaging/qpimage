import abc
import numbers
import warnings

import h5py
import numpy as np

from . import bg_estimate

#: default hdf5 compression method
COMPRESSION = "gzip"

#: valid background data identifiers
VALID_BG_KEYS = ["data",
                 "fit",
                 ]


class ImageData(object):
    """Base class for image management

    See Also
    --------
    Amplitude: ImageData with amplitude background correction
    Phase: ImageData with phase background correction
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, h5):
        """
        Parameters
        ----------
        h5: h5py.Group
            HDF5 group where all data is kept
        """
        self.h5 = h5
        if "bg_data" not in self.h5:
            self.h5.create_group("bg_data")

    def __repr__(self):
        name = self.__class__.__name__
        rep = "{name} image, {x}x{y}px".format(name=name,
                                               x=self.raw.shape[0],
                                               y=self.raw.shape[1],
                                               )
        return rep

    def __setitem__(self, key, value):
        if key in self.h5:
            del self.h5[key]
        if value is not None:
            dset = self.h5.create_dataset(key,
                                          data=value,
                                          fletcher32=True,
                                          compression=COMPRESSION)
            # Create and Set image attributes
            # HDFView recognizes this as a series of images
            dset.attrs.create('CLASS', b'IMAGE')
            dset.attrs.create('IMAGE_VERSION', b'1.2')
            dset.attrs.create('IMAGE_SUBCLASS', b'IMAGE_GRAYSCALE')

    @abc.abstractmethod
    def _bg_combine(self, *bgs):
        """Combine several background images"""

    @abc.abstractmethod
    def _bg_correct(self, raw, bg):
        """Remove `bg` from `raw` image data"""

    @property
    def bg(self):
        """combined background image data"""
        return self._bg_combine(self.h5["bg_data"].values())

    @property
    def image(self):
        """background corrected image data"""
        return self._bg_correct(self.raw, self.bg)

    @property
    def info(self):
        """list of background correction parameters"""
        info = []
        name = self.__class__.__name__.lower()
        # get bg information
        for key in VALID_BG_KEYS:
            if key in self.h5["bg_data"]:
                attrs = self.h5["bg_data"][key].attrs
                for akey in attrs:
                    atr = attrs[akey]
                    var = "{} background {}".format(name, akey)
                    info.append((var, atr))
        if "fit" in self.h5["bg_data"]:
            # binary background
            var_bin = "{} background from binary".format(name)
            if ("estimate_bg_from_binary" in self.h5 and
                    self.h5["estimate_bg_from_binary"] is not None):
                # bg was computed from binary image
                info.append((var_bin, True))
            else:
                info.append((var_bin, False))
        return info

    @property
    def raw(self):
        """raw (uncorrected) image data"""
        return self.h5["raw"].value

    def del_bg(self, key):
        """Remove the background image data

        Parameters
        ----------
        key: str
            One of :const:`VALID_BG_KEYS`
        """
        if key not in VALID_BG_KEYS:
            raise ValueError("Invalid bg key: {}".format(key))
        if key in self.h5["bg_data"]:
            del self.h5["bg_data"][key]
        else:
            msg = "No bg data to clear for '{}' in {}.".format(key, self)
            warnings.warn(msg)

    def estimate_bg(self, fit_offset="mean", fit_profile="tilt",
                    border_px=0, from_binary=None, ret_binary=False):
        """Estimate image background

        Parameters
        ----------
        fit_profile: str
            The type of background profile to fit:

            - "offset": offset only
            - "poly2o": 2D 2nd order polynomial with mixed terms
            - "tilt": 2D linear tilt with offset (default)
        fit_offset: str
            The method for computing the profile offset

            - "fit": offset as fitting parameter
            - "gauss": center of a gaussian fit
            - "mean": simple average
            - "mode": mode (see `qpimage.bg_estimate.mode`)
        border_px: float
            Assume that a frame of `border_px` pixels around
            the image is background.
        from_binary: boolean np.ndarray or None
            Use a boolean array to define the background area.
            The binary image must have the same shape as the
            input data.`True` elements are used for background
            estimation.
        ret_binary: bool
            Return the binary image used to compute the background.

        Notes
        -----
        If both `border_px` and `from_binary` are given, the
        intersection of the two resulting binary images is used.

        The arguments passed to this method are stored in the
        hdf5 file `self.h5` and are used for optional integrity
        checking using `qpimage.integrity_check.check`.

        See Also
        --------
        qpimage.bg_estimate.estimate
        """
        # remove existing bg before accessing imdat.image
        self.set_bg(bg=None, key="fit")
        # compute bg
        bgimage, binary = bg_estimate.estimate(data=self.image,
                                               fit_offset=fit_offset,
                                               fit_profile=fit_profile,
                                               border_px=border_px,
                                               from_binary=from_binary,
                                               ret_binary=True)
        attrs = {"fit_offset": fit_offset,
                 "fit_profile": fit_profile,
                 "border_px": border_px}
        self.set_bg(bg=bgimage, key="fit", attrs=attrs)
        # save `from_binary` separately (arrays vs. h5 attributes)
        # (if `from_binary` is `None`, this will remove the array)
        self["estimate_bg_from_binary"] = from_binary
        # return binary image
        if ret_binary:
            return binary

    def get_bg(self, key=None, ret_attrs=False):
        """Get the background data

        Parameters
        ----------
        key: None or str
            A user-defined key that identifies the background data.
            Examples are "data" for experimental data, or "fit"
            for an estimated background correction
            (see :const:`VALID_BG_KEYS`). If set to `None`,
            returns the combined background image (:const:`ImageData.bg`).
        ret_attrs: bool
            Also returns the attributes of the background data.
        """
        if key is None:
            if ret_attrs:
                raise ValueError("No attributes for combined background!")
            return self.bg
        else:
            if key not in VALID_BG_KEYS:
                raise ValueError("Invalid bg key: {}".format(key))
            if key in self.h5["bg_data"]:
                data = self.h5["bg_data"][key].value
                if ret_attrs:
                    attrs = dict(self.h5["bg_data"][key].attrs)
                    # remove keys for image visualization in hdf5 files
                    for h5k in ["CLASS", "IMAGE_VERSION", "IMAGE_SUBCLASS"]:
                        if h5k in attrs:
                            attrs.pop(h5k)
                    ret = (data, attrs)
                else:
                    ret = data
            else:
                raise KeyError("No background data for {}!".format(key))
            return ret

    def set_bg(self, bg, key="data", attrs={}):
        """Set the background data

        Parameters
        ----------
        bg: numbers.Real, 2d ndarray, ImageData, or h5py.Dataset
            The background data. If `bg` is an `h5py.Dataset` object,
            it must exist in the same hdf5 file (a hard link is created).
            If set to `None`, the data will be removed.
        key: str
            One of :const:`VALID_BG_KEYS`)
        attrs: dict
            List of background attributes

        See Also
        --------
        del_bg: removing background data
        """
        if key not in VALID_BG_KEYS:
            raise ValueError("Invalid bg key: {}".format(key))
        # remove previous background key
        if key in self.h5["bg_data"]:
            del self.h5["bg_data"][key]
        # set background
        if isinstance(bg, (numbers.Real, np.ndarray)):
            dset = self.h5["bg_data"].create_dataset(key,
                                                     data=bg,
                                                     fletcher32=True,
                                                     compression=COMPRESSION)
            # Create and Set image attributes
            # HDFView recognizes this as a series of images
            dset.attrs.create('CLASS', b'IMAGE')
            dset.attrs.create('IMAGE_VERSION', b'1.2')
            dset.attrs.create('IMAGE_SUBCLASS', b'IMAGE_GRAYSCALE')
            for kw in attrs:
                self.h5["bg_data"][key].attrs[kw] = attrs[kw]
        elif isinstance(bg, h5py.Dataset):
            # Create a hard link
            # (This functionality was intended for saving memory when storing
            # large QPSeries with universal background data, i.e. when using
            # `QPSeries.add_qpimage` with the `bg_from_idx` keyword.)
            self.h5["bg_data"][key] = bg
        elif bg is not None:
            msg = "Unknown background data type: {}".format(bg)
            raise ValueError(msg)


class Amplitude(ImageData):
    """Dedicated class for amplitude image data

    For amplitude image data, background correction is defined
    by dividing the raw image by the background image.
    """

    def _bg_combine(self, bgs):
        """Combine several background amplitude images"""
        out = np.ones(self.h5["raw"].shape, dtype=float)
        # Use indexing ([:]), because bg is an h5py.DataSet
        for bg in bgs:
            out *= bg.value
        return out

    def _bg_correct(self, raw, bg):
        """Remove background from raw amplitude image"""
        return raw / bg


class Phase(ImageData):
    """Dedicated class for phase image data

    For phase image data, background correction is defined
    by subtracting the background image from the raw image.
    """

    def _bg_combine(self, bgs):
        """Combine several background phase images"""
        out = np.zeros(self.h5["raw"].shape, dtype=float)
        for bg in bgs:
            # Use .value attribute, because bg is an h5py.DataSet
            out += bg.value
        return out

    def _bg_correct(self, raw, bg):
        """Remove background from raw phase image"""
        return raw - bg
