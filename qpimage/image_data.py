import abc

import numpy as np


class ImageData(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, h5):
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
        self.h5[key] = value

    @abc.abstractmethod
    def _bg_combine(self, *bgs):
        """Combine several background images"""

    @abc.abstractmethod
    def _bg_correct(self, raw, bg):
        """Remove `bg` from `raw` image data"""

    def _reset_bg(self):
        """Reset bg correction (force computation of image data)"""
        for key in ["image", "bg"]:
            if key in self.h5:
                del self.h5[key]

    @property
    def bg(self):
        """The combined background image data"""
        return self._bg_combine(self.h5["bg_data"].values())

    @property
    def image(self):
        """The background corrected image data"""
        return self._bg_correct(self.raw, self.bg)

    @property
    def raw(self):
        return self.h5["raw"].value

    def set_bg(self, bg, key="data"):
        """Set the background data

        Parameters
        ----------
        bg: int, float, 2d ndarray, or same subclass of ImageData
            The background data. If set to `None`, the data will be
            removed.
        key: str
            A user-defined key that identifies the background data.
            Examples are "data" for experimental data, or "ramp"
            for a ramp background correction. There are no
            restrictions regarding key names.
        """
        reset = False
        # remove previous background key
        if key in self.h5["bg_data"]:
            del self.h5["bg_data"][key]
            reset = True
        # set background
        if bg is not None:
            msg = "`bg` must be scalar or ndarray"
            assert isinstance(bg, (float, int, np.ndarray)), msg
            self.h5["bg_data"][key] = bg
            reset = True
        # reset computed data
        if reset:
            self._reset_bg()


class Amplitude(ImageData):
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
