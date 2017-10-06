import h5py
import numpy as np
from skimage.restoration import unwrap_phase

from . import bg_estimate
from .image_data import Amplitude, Phase
from .meta import MetaDict
from ._version import version as __version__


class QPImage(object):
    def __init__(self, data=None, bg_data=None, which_data="phase",
                 meta_data={}, hdf5_file=None, hdf5_mode="a"
                 ):
        """Quantitative phase image manipulation

        This class implements various tasks for quantitative phase
        imaging, including phase unwrapping, background correction,
        numerical focusing, and data export.

        Parameters
        ----------
        data: 2d ndarray (float or complex) or list
            The experimental data (see `which_data`)
        bg_data: 2d ndarray (float or complex), list, or `None`
            The background data (must be same type as `data`)
        which_data: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object with
            the phase data as first element.
        meta_data: dict
            Meta data associated with the input data.
            see :py:class:`qpimage.VALID_META_KEYS`
        hdf5_file: str or None
            A path to an hdf5 data file where all data is cached. If
            set to `None` (default), all data will be handled in
            memory using the "core" driver of the :mod:`h5py`'s
            :class:`h5py:File` class. If the file does not exist,
            it is created. If the file already exists, it is opened
            with the file mode defined by `hdf5_mode`.
        hdf5_mode: str
            Valid file modes are:
              - "r": Readonly, file must exist
              - "r+": Read/write, file must exist
              - "w": Create file, truncate if exists
              - "w-" or "x": Create file, fail if exists
              - "a": Read/write if exists, create otherwise (default)
        """
        if hdf5_file is None:
            h5kwargs = {"name": "none.h5",
                        "driver": "core",
                        "backing_store": False,
                        "mode": "a"}
        else:
            h5kwargs = {"name": hdf5_file,
                        "mode": hdf5_mode}
        self.h5 = h5py.File(**h5kwargs)

        for group in ["amplitude", "phase"]:
            if group not in self.h5:
                self.h5.create_group(group)

        self._amp = Amplitude(self.h5["amplitude"])
        self._pha = Phase(self.h5["phase"])

        if data is not None:
            # compute phase and amplitude from input data
            amp, pha = self._get_amp_pha(data=data,
                                         which_data=which_data)
            self._amp["raw"] = amp
            self._pha["raw"] = pha

            # set background data
            self.set_bg_data(bg_data=bg_data,
                             which_data=which_data)
        # set meta data
        meta = MetaDict(meta_data)
        for key in meta:
            if meta[key]:
                self.h5.attrs[key] = meta[key]
        if "qpimage version" not in self.h5.attrs:
            self.h5.attrs["qpimage version"] = __version__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.h5.flush()
        self.h5.close()

    def __repr__(self):
        rep = "QPImage, {x}x{y}px".format(x=self._amp.raw.shape[0],
                                          y=self._amp.raw.shape[1],
                                          )
        if "wavelength" in self.h5.attrs:
            wl = self.h5.attrs["wavelength"]
            if wl < 2000e-9 and wl > 10e-9:
                # convenience for light microscopy
                rep += ", λ={:.1f}nm".format(wl * 1e9)
            else:
                rep += ", λ={:.2e}m".format(wl)

        return rep

    def _get_amp_pha(self, data, which_data):
        """Convert input data to phase and amplitude

        Parameters
        ----------
        data: 2d ndarray (float or complex) or list
            The experimental data (see `which_data`)
        which_data: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object with
            the phase data as first element.

        Returns
        -------
        amp, pha: tuple of (:py:class:`Amplitdue`, :py:class:`Phase`)
        """
        assert which_data in ["field", "phase", "phase,amplitude",
                              "phase,intensity"]
        if which_data == "field":
            amp = np.abs(data)
            pha = unwrap_phase(np.angle(data))
        elif which_data == "phase":
            amp = np.ones_like(data)
            pha = unwrap_phase(data)
        elif which_data == "phase,amplitude":
            pha = unwrap_phase(data[0])
            amp = data[1]
        elif which_data == "phase,intensity":
            pha = unwrap_phase(data[0])
            amp = np.sqrt(data[1])
        return amp, pha

    @property
    def bg_amp(self):
        """background amplitude image"""
        return self._amp.bg

    @property
    def bg_pha(self):
        """background phase image"""
        return self._pha.bg

    @property
    def amp(self):
        """background-corrected amplitude image"""
        return self._amp.image

    @property
    def field(self):
        """background-corrected complex field"""
        return self.amp * np.exp(1j * self.pha)

    @property
    def meta(self):
        """meta data"""
        return MetaDict(self.h5.attrs)

    @property
    def pha(self):
        """background-corrected phase image"""
        return self._pha.image

    @property
    def shape(self):
        """the shape of the image"""
        return self._pha.h5["raw"].shape

    def clear_bg(self, which_data=["amplitude", "phase"], keys="fit"):
        """Clear background correction

        Parameters
        ----------
        which_data: str or list of str
            From which type of data to remove the background
            information. The list contains either "amplitude",
            "phase", or both.
        keys: str or list of str
            Which type of background data to remove. One of:
              - "fit": the background data computed with
                :py:func:`qpimage.QPImage.compute_bg`
              - "data": the experimentally obtained background image

        """
        # convert to list
        if isinstance(which_data, str):
            which_data = [which_data]
        if isinstance(keys, str):
            keys = [keys]
        # Get image data for clearing
        imdats = []
        if "amplitude" in which_data:
            imdats.append(self._amp)
        if "phase" in which_data:
            imdats.append(self._pha)
        if not imdats:
            msg = "`which_data` must contain 'phase' or 'amplitude'!"
            raise ValueError(msg)
        # Perform clearing of backgrounds
        for imdat in imdats:
            for key in keys:
                imdat.set_bg(None, key)

    def compute_bg(self, which_data="phase",
                   fit_offset="average", fit_profile="ramp",
                   border_m=0, border_perc=0, border_px=0,
                   from_binary=None, ret_binary=False):
        """Compute background correction

        Parameters
        ----------
        which_data: str or list of str
            From which type of data to remove the background
            information. The list contains either "amplitude",
            "phase", or both.
        fit_profile: str
            The type of background profile to fit:
              - "ramp": 2D linear ramp with offset (default)
              - "offset": offset only
        fit_offset: str
            The method for computing the profile offset
              - "fit": offset as fitting parameter
              - "gauss": center of a gaussian fit
              - "mean": simple average
              - "mode": mode (see `qpimage.bg_estimate.mode`)
        border_m: float
            Assume that a frame of `border_m` meters around the
            image is background. The value is converted to
            pixels and rounded.
        border_perc: float
            Assume that a frame of `border_perc` percent around
            the image is background. The value is converted to
            pixels and rounded. If the aspect ratio of the image
            is not one, then the average of the data's shape is
            used to compute the percentage in pixels.
        border_px: float
            Assume that a frame of `border_px` pixels around
            the image is background.
        from_binary: boolean np.ndarray or None
            Use a boolean array to define the background area.
            The binary image must have the same shape as the
            input data.
        ret_binary: bool
            Return the binary image used to compute the background.

        Notes
        -----
        The `border_*` values are translated to pixel values and
        the largest pixel border is used to generate a binary
        image for background computation.

        If any of the `border_*` arguments are non-zero and
        `from_binary` is given, the intersection of the two
        resulting binary images is used.
        """
        # convert to list
        if isinstance(which_data, str):
            which_data = [which_data]
        # check validity
        if not ("amplitude" in which_data or
                "phase" in which_data):
            msg = "`which_data` must contain 'phase' or 'amplitude'!"
            raise ValueError(msg)
        # get border in px
        border_list = []
        if border_m > 0:
            border_list.append(border_m / self.meta["pixel size"])
        if border_perc > 0:
            size = np.average(self.shape)
            border_list.append(size * border_perc / 100)
        if border_px:
            border_list.append(border_px)
        border_px = np.int(np.round(np.max(border_list)))
        # Get affected image data
        imdat_list = []
        if "amplitude" in which_data:
            imdat_list.append(self._amp)
        if "phase" in which_data:
            imdat_list.append(self._pha)
        # Perform correction
        for imdat in imdat_list:
            # remove existing bg
            imdat.set_bg(bg=None, key="fit")
            # compute bg
            bgimage, binary = bg_estimate.estimate(data=imdat.image,
                                                   fit_offset=fit_offset,
                                                   fit_profile=fit_profile,
                                                   border_px=border_px,
                                                   from_binary=from_binary,
                                                   ret_binary=True)
            imdat.set_bg(bg=bgimage, key="fit")
            # set meta data attributes
        if ret_binary:
            return binary

    def refocus(self, distance, method="helmholtz"):
        """Numerically refocus the current field

        Parameters
        ----------
        distance: float
            Focusing distance [m]
        method: str
            Refocusing method, one of ["helmholtz","fresnel"]

        See Also
        --------
        :mod:`nrefocus` library used for numerical focusing
        """
        # TODO:
        # - Perform refocusing and create new image data instances
        # - Remember old image data instances
        # - Maybe return a new instance of QPImage
        # - Allow autofocusing?

    def set_bg_data(self, bg_data, which_data):
        """Set background amplitude and phase data

        Parameters
        ----------
        bg_data: 2d ndarray (float or complex), list, or `None`
            The background data (must be same type as `data`).
            If set to `None`, the background data is reset.
        which_data: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object with
            the phase data as first element.
        """
        if bg_data is None:
            # Reset phase and amplitude
            amp, pha = None, None
        else:
            # Compute phase and amplitude from data and which_data
            amp, pha = self._get_amp_pha(bg_data, which_data)
        # Set background data
        self._amp.set_bg(amp, key="data")
        self._pha.set_bg(pha, key="data")
