import pathlib

import h5py
import nrefocus
import numpy as np
from skimage.restoration import unwrap_phase

from . import holo
from .image_data import Amplitude, Phase, write_image_dataset
from .meta import MetaDict, META_KEYS
from ._version import version as __version__

#: valid combinations for keyword argument `which_data`
VALID_INPUT_DATA = ["field",
                    "hologram",
                    "phase",
                    ("phase", "amplitude"),
                    ("phase", "intensity"),
                    ]


class QPImage(object):
    # required to create in-memory hdf5 files with unique fd
    _instances = 0

    def __init__(self, data=None, bg_data=None, which_data="phase",
                 meta_data={}, holo_kw={}, h5file=None, h5mode="a",
                 h5dtype="float32",
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
            "hologram", "field", "phase", "phase,amplitude",
            or "phase,intensity", where the latter two require an
            indexable object with the phase data as first element.
        meta_data: dict
            Meta data associated with the input data.
            see :class:`qpimage.meta.META_KEYS`
        holo_kw: dict
            Special keyword arguments for phase retrieval from
            hologram data (`which_data="hologram"`).
            See :func:`qpimage.holo.get_field` for valid keyword
            arguments.

            .. versionadded:: 0.1.6
        h5file: str, pathlib.Path, h5py.Group, h5py.File, or None
            A path to an hdf5 data file where all data is cached. If
            set to `None` (default), all data will be handled in
            memory using the "core" driver of the :mod:`h5py`'s
            :class:`h5py:File` class. If the file does not exist,
            it is created. If the file already exists, it is opened
            with the file mode defined by `hdf5_mode`. If this is
            an instance of h5py.Group or h5py.File, then this will
            be used to internally store all data.
        h5mode: str
            Valid file modes are (only applies if `h5file` is a path)

            - "r": Readonly, file must exist
            - "r+": Read/write, file must exist
            - "w": Create file, truncate if exists
            - "w-" or "x": Create file, fail if exists
            - "a": Read/write if exists, create otherwise (default)

        h5dtype: str
            The datatype in which to store the image data. The default
            is "float32" which is sufficient for 2D image analysis and
            consumes only half the disk space of the numpy default
            "float64".

        Notes
        -----
        QPImage is slicable; the following returns a new QPImage with
        the same meta data, but with all background corrections merged
        into the raw data:

        .. code-block:: python

            qpi = QPImage(data=...)
            qpi_scliced = qpi[10:20, 40:30]
        """
        if (data is not None and
                not isinstance(data, (np.ndarray, list, tuple))):
            msg = "`data` must be numpy.ndarray!"
            if isinstance(data, (str, pathlib.Path)):
                msg += " Did you mean `h5file={}`?".format(data)
            raise ValueError(msg)
        if isinstance(h5file, h5py.Group):
            self.h5 = h5file
            self._do_h5_cleanup = False
        else:
            if h5file is None:
                h5kwargs = {"name": "qpimage{}.h5".format(QPImage._instances),
                            "driver": "core",
                            "backing_store": False,
                            "mode": "a"}
            else:
                h5kwargs = {"name": h5file,
                            "mode": h5mode}
            self.h5 = h5py.File(**h5kwargs)
            self._do_h5_cleanup = True
        QPImage._instances += 1
        # set holo data
        self.holo_kw = holo_kw
        # set meta data
        meta = MetaDict(meta_data)
        for key in meta:
            self.h5.attrs[key] = meta[key]
        if "qpimage version" not in self.h5.attrs:
            self.h5.attrs["qpimage version"] = __version__
        # set data
        for group in ["amplitude", "phase"]:
            if group not in self.h5:
                self.h5.create_group(group)
        self._amp = Amplitude(self.h5["amplitude"], h5dtype=h5dtype)
        self._pha = Phase(self.h5["phase"], h5dtype=h5dtype)
        if data is not None:
            # compute phase and amplitude from input data
            amp, pha = self._get_amp_pha(data=data,
                                         which_data=which_data)
            self._amp["raw"] = amp
            self._pha["raw"] = pha
            # set background data
            self.set_bg_data(bg_data=bg_data,
                             which_data=which_data)
        self.h5dtype = h5dtype

    def __enter__(self):
        return self

    def __eq__(self, other):
        if (isinstance(other, QPImage) and
            self.shape == other.shape and
            np.allclose(self.amp, other.amp) and
            np.allclose(self.pha, other.pha) and
                self.meta == other.meta):
            return True
        else:
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._do_h5_cleanup:
            self.h5.flush()
            self.h5.close()

    def __contains__(self, key):
        return key in self.h5.attrs

    def __getitem__(self, given):
        """Slice QPImage `pha` and `amp` and return a new QPImage

        The QPImage returned by this method is background-
        corrected, i.e. it is not possible to reproduce the
        background correction of the original QPImage.
        """
        if isinstance(given, (slice, tuple)):
            # return new QPImage
            pha = self.pha.__getitem__(given)
            amp = self.amp.__getitem__(given)
            qpi = QPImage(data=(pha, amp),
                          which_data=("phase", "amplitude"),
                          meta_data=self.meta)
            return qpi
        elif isinstance(given, str):
            # return meta data
            return self.meta[given]
        else:
            msg = "Only slicing and meta data keys allowed for `__getitem__`"
            raise ValueError(msg)

    def __repr__(self):
        if "identifier" in self:
            ident = " '{}'".format(self["identifier"])
        else:
            ident = ""
        rep = "QPImage{}, {x}x{y}px".format(ident,
                                            x=self._amp.raw.shape[0],
                                            y=self._amp.raw.shape[1],
                                            )
        if "wavelength" in self:
            wl = self["wavelength"]
            if wl < 2000e-9 and wl > 10e-9:
                # convenience for light microscopy
                rep += ", λ={:.1f}nm".format(wl * 1e9)
            else:
                rep += ", λ={:.2e}m".format(wl)

        return rep

    def __setitem__(self, key, value):
        if key not in META_KEYS:
            raise KeyError("Unknown meta data key: {}".format(key))
        else:
            self.h5.attrs[key] = value

    @staticmethod
    def _conv_which_data(which_data):
        """Convert which data to string or tuple

        This function improves user convenience,
        as `which_data` may be of several types
        (str, ,str with spaces and commas, list, tuple) which
        is internally handled by this method.
        """
        if isinstance(which_data, str):
            which_data = which_data.lower().strip()
            if which_data.count(","):
                # convert comma string to list
                which_data = [w.strip() for w in which_data.split(",")]
                # remove empty strings
                which_data = [w for w in which_data if w]
                if len(which_data) == 1:
                    return which_data[0]
                else:
                    # convert to tuple
                    return tuple(which_data)
            else:
                return which_data
        elif isinstance(which_data, (list, tuple)):
            which_data = [w.lower().strip() for w in which_data]
            return tuple(which_data)
        elif which_data is None:
            return None
        else:
            msg = "unknown type for `which_data`: {}".format(which_data)
            raise ValueError(msg)

    def _get_amp_pha(self, data, which_data):
        """Convert input data to phase and amplitude

        Parameters
        ----------
        data: 2d ndarray (float or complex) or list
            The experimental data (see `which_data`)
        which_data: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "hologram", "phase,amplitude", or
            "phase,intensity", where the latter two require an
            indexable object with the phase data as first element.

        Returns
        -------
        amp, pha: tuple of (:class:`Amplitdue`, :class:`Phase`)
        """
        which_data = QPImage._conv_which_data(which_data)
        if which_data not in VALID_INPUT_DATA:
            msg = "`which_data` must be one of {}!".format(VALID_INPUT_DATA)
            raise ValueError(msg)

        if which_data == "field":
            amp = np.abs(data)
            pha = np.angle(data)
        elif which_data == "phase":
            pha = data
            amp = np.ones_like(data)
        elif which_data == ("phase", "amplitude"):
            amp = data[1]
            pha = data[0]
        elif which_data == ("phase", "intensity"):
            amp = np.sqrt(data[1])
            pha = data[0]
        elif which_data == "hologram":
            amp, pha = self._get_amp_pha(holo.get_field(data, **self.holo_kw),
                                         which_data="field")
        if amp.size == 0 or pha.size == 0:
            msg = "`data` with shape {} has zero size!".format(amp.shape)
            raise ValueError(msg)
        # phase unwrapping (take into account nans)
        nanmask = np.isnan(pha)
        if np.sum(nanmask):
            # create masked array
            # skimage.restoration.unwrap_phase cannot handle nan data
            # (even if masked)
            pham = pha.copy()
            pham[nanmask] = 0
            pham = np.ma.masked_array(pham, mask=nanmask)
            pha = unwrap_phase(pham, seed=47)
            pha[nanmask] = np.nan
        else:
            pha = unwrap_phase(pha, seed=47)

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
    def info(self):
        """list of tuples with QPImage meta data"""
        info = []
        # meta data
        meta = self.meta
        for key in meta:
            info.append((key, self.meta[key]))
        # background correction
        for imdat in [self._amp, self._pha]:
            info += imdat.info
        return info

    @property
    def meta(self):
        """dictionary with imaging meta data"""
        return MetaDict(self.h5.attrs)

    @property
    def pha(self):
        """background-corrected phase image"""
        return self._pha.image

    @property
    def raw_amp(self):
        """raw amplitude image"""
        return self._amp.raw

    @property
    def raw_pha(self):
        """raw phase image"""
        return self._pha.raw

    @property
    def shape(self):
        """size of image dimensions"""
        return self._pha.h5["raw"].shape

    def clear_bg(self, which_data=("amplitude", "phase"), keys="fit"):
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
              :func:`qpimage.QPImage.compute_bg`
            - "data": the experimentally obtained background image
        """
        which_data = QPImage._conv_which_data(which_data)
        if isinstance(keys, str):
            # make sure keys is a list of strings
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
                imdat.del_bg(key)

    def compute_bg(self, which_data="phase",
                   fit_offset="mean", fit_profile="tilt",
                   border_m=0, border_perc=0, border_px=0,
                   from_mask=None, ret_mask=False):
        """Compute background correction

        Parameters
        ----------
        which_data: str or list of str
            From which type of data to remove the background
            information. The list contains either "amplitude",
            "phase", or both.
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
        from_mask: boolean np.ndarray or None
            Use a boolean array to define the background area.
            The boolean mask must have the same shape as the
            input data. `True` elements are used for background
            estimation.
        ret_mask: bool
            Return the boolean mask used to compute the background.

        Notes
        -----
        The `border_*` values are translated to pixel values and
        the largest pixel border is used to generate a mask
        image for background computation.

        If any of the `border_*` arguments are non-zero and
        `from_mask` is given, the intersection of the two
        is used, i.e. the positions where both, the frame
        mask and `from_mask`, are `True`.

        See Also
        --------
        qpimage.bg_estimate.estimate
        """
        which_data = QPImage._conv_which_data(which_data)
        # check validity
        if not ("amplitude" in which_data or
                "phase" in which_data):
            msg = "`which_data` must contain 'phase' or 'amplitude'!"
            raise ValueError(msg)
        # get border in px
        border_list = []
        if border_m:
            if border_m < 0:
                raise ValueError("`border_m` must be greater than zero!")
            border_list.append(border_m / self.meta["pixel size"])
        if border_perc:
            if border_perc < 0 or border_perc > 50:
                raise ValueError("`border_perc` must be in interval [0, 50]!")
            size = np.average(self.shape)
            border_list.append(size * border_perc / 100)
        if border_px:
            border_list.append(border_px)
        # get maximum border size
        if border_list:
            border_px = np.int(np.round(np.max(border_list)))
        elif from_mask is None:
            raise ValueError("Neither `from_mask` nor `border_*` given!")
        elif np.all(from_mask == 0):
            raise ValueError("`from_mask` must not be all-zero!")
        # Get affected image data
        imdat_list = []
        if "amplitude" in which_data:
            imdat_list.append(self._amp)
        if "phase" in which_data:
            imdat_list.append(self._pha)
        # Perform correction
        for imdat in imdat_list:
            mask = imdat.estimate_bg(fit_offset=fit_offset,
                                     fit_profile=fit_profile,
                                     border_px=border_px,
                                     from_mask=from_mask,
                                     ret_mask=ret_mask)
        return mask

    def copy(self, h5file=None):
        """Create a copy of the current instance

        This is done by recursively copying the underlying hdf5 data.

        Parameters
        ----------
        h5file: str, h5py.File, h5py.Group, or None
            see `QPImage.__init__`
        """
        h5 = copyh5(self.h5, h5file)
        return QPImage(h5file=h5, h5dtype=self.h5dtype)

    def refocus(self, distance, method="helmholtz", h5file=None, h5mode="a"):
        """Compute a numerically refocused QPImage

        Parameters
        ----------
        distance: float
            Focusing distance [m]
        method: str
            Refocusing method, one of ["helmholtz","fresnel"]
        h5file: str, h5py.Group, h5py.File, or None
            A path to an hdf5 data file where the QPImage is cached.
            If set to `None` (default), all data will be handled in
            memory using the "core" driver of the :mod:`h5py`'s
            :class:`h5py:File` class. If the file does not exist,
            it is created. If the file already exists, it is opened
            with the file mode defined by `hdf5_mode`. If this is
            an instance of h5py.Group or h5py.File, then this will
            be used to internally store all data.
        h5mode: str
            Valid file modes are (only applies if `h5file` is a path)

            - "r": Readonly, file must exist
            - "r+": Read/write, file must exist
            - "w": Create file, truncate if exists
            - "w-" or "x": Create file, fail if exists
            - "a": Read/write if exists, create otherwise (default)

        Returns
        -------
        qpi: qpimage.QPImage
            Refocused phase and amplitude data

        See Also
        --------
        :mod:`nrefocus`: library used for numerical focusing
        """
        field2 = nrefocus.refocus(field=self.field,
                                  d=distance/self["pixel size"],
                                  nm=self["medium index"],
                                  res=self["wavelength"]/self["pixel size"],
                                  method=method
                                  )
        if "identifier" in self:
            ident = self["identifier"]
        else:
            ident = ""
        meta_data = self.meta
        meta_data["identifier"] = "{}@{}{:.5e}m".format(ident,
                                                        method[0],
                                                        distance)
        qpi2 = QPImage(data=field2,
                       which_data="field",
                       meta_data=meta_data,
                       h5file=h5file,
                       h5mode=h5mode)
        return qpi2

    def set_bg_data(self, bg_data, which_data=None):
        """Set background amplitude and phase data

        Parameters
        ----------
        bg_data: 2d ndarray (float or complex), list, QPImage, or `None`
            The background data (must be same type as `data`).
            If set to `None`, the background data is reset.
        which_data: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object for
            `bg_data` with the phase data as first element.
        """
        if isinstance(bg_data, QPImage):
            if which_data is not None:
                msg = "`which_data` must not be set if `bg_data` is QPImage!"
                raise ValueError(msg)
            pha, amp = bg_data.pha, bg_data.amp
        elif bg_data is None:
            # Reset phase and amplitude
            amp, pha = None, None
        else:
            # Compute phase and amplitude from data and which_data
            amp, pha = self._get_amp_pha(bg_data, which_data)
        # Set background data
        self._amp.set_bg(amp, key="data")
        self._pha.set_bg(pha, key="data")


def copyh5(inh5, outh5):
    """Recursively copy all hdf5 data from one group to another

    Parameters
    ----------
    inh5: str, h5py.File, or h5py.Group
        The input hdf5 data. This can be either a file name or
        an hdf5 object.
    outh5: str, h5py.File, h5py.Group, or None
        The output hdf5 data. This can be either a file name or
        an hdf5 object. If set to `None`, a new hdf5 object is
        created in memory.

    Notes
    -----
    All data in outh5 are overridden by the inh5 data.
    """
    if not isinstance(inh5, h5py.Group):
        inh5 = h5py.File(inh5, mode="r")
    if outh5 is None:
        # create file in memory
        h5kwargs = {"name": "qpimage{}.h5".format(QPImage._instances),
                    "driver": "core",
                    "backing_store": False,
                    "mode": "a"}
        outh5 = h5py.File(**h5kwargs)
        return_h5obj = True
        QPImage._instances += 1
    elif not isinstance(outh5, h5py.Group):
        # create new file
        outh5 = h5py.File(outh5, mode="w")
        return_h5obj = False
    else:
        return_h5obj = True
    # begin iteration
    for key in inh5:
        if key in outh5:
            del outh5[key]
        if isinstance(inh5[key], h5py.Group):
            outh5.create_group(key)
            copyh5(inh5[key], outh5[key])
        else:
            dset = write_image_dataset(group=outh5,
                                       key=key,
                                       data=inh5[key].value,
                                       h5dtype=inh5[key].dtype)
            dset.attrs.update(inh5[key].attrs)
    outh5.attrs.update(inh5.attrs)
    if return_h5obj:
        # in-memory or previously created instance of h5py.File
        return outh5
    else:
        # properly close the file and return its name
        fn = outh5.filename
        outh5.flush()
        outh5.close()
        return fn
