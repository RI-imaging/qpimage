import h5py
import numpy as np

from .core import QPImage
from .meta import DATA_KEYS


class IntegrityCheckError(BaseException):
    """Raised when a QPImage data set is incomplete or corrupt"""
    pass


def check(qpi_or_h5file, checks=["attributes", "background"]):
    """Checks various properties of a :class:`qpimage.core.QPImage` instance

    Parameters
    ----------
    qpi_or_h5file: qpimage.core.QPImage or str
        A QPImage object or a path to an hdf5 file
    checks: list of str
        Which checks to perform ("attributes" and/or "background")

    Raises
    ------
    IntegrityCheckError
        if the checks fail
    """
    if isinstance(checks, str):
        checks = [checks]
    for ch in checks:
        if ch not in ["attributes", "background"]:
            raise ValueError("Unknown check: {}".format(check))

    if isinstance(qpi_or_h5file, QPImage):
        qpi = qpi_or_h5file
    else:
        qpi = QPImage(h5file=qpi_or_h5file, h5mode="r")

    # check attributes
    if "attributes" in checks:
        check_attributes(qpi)

    # check background estimation
    if "background" in checks:
        check_background(qpi)


def check_attributes(qpi):
    """Check QPimage attributes

    Parameters
    ----------
    qpi: qpimage.core.QPImage

    Raises
    ------
    IntegrityCheckError
        if the check fails
    """
    missing_attrs = []
    for key in DATA_KEYS:
        if key not in qpi.meta:
            missing_attrs.append(key)
    if missing_attrs:
        msg = "Attributes are missing: {} ".format(missing_attrs) \
            + "in {}!".format(qpi)
        raise IntegrityCheckError(msg)


def check_background(qpi):
    """Check QPimage background data

    Parameters
    ----------
    qpi: qpimage.core.QPImage

    Raises
    ------
    IntegrityCheckError
        if the check fails
    """
    for imdat in [qpi._amp, qpi._pha]:
        try:
            fit, attrs = imdat.get_bg(key="fit", ret_attrs=True)
        except KeyError:
            # No bg correction performed
            pass
        else:
            kwargs = dict(attrs)
            # check if we have a user-defined mask image
            binkey = "estimate_bg_from_mask"
            if binkey in imdat.h5:
                kwargs["from_mask"] = imdat.h5[binkey].value
            else:
                kwargs["from_mask"] = None
            # compute background correction
            with h5py.File("check.h5",
                           driver="core",
                           backing_store=False) as h5:
                # imdat.__class__ is "Amplitude" or "Phase"
                testimdat = imdat.__class__(h5)
                testimdat["raw"] = imdat.raw
                # Set experimental bg data if given
                try:
                    bg = imdat.get_bg("data")
                except KeyError:
                    pass
                else:
                    testimdat.set_bg(bg, key="data")
                # fit bg
                testimdat.estimate_bg(**kwargs)
                # compare
                if not np.allclose(testimdat.get_bg(key="fit"), fit):
                    msg = "Wrong estimated (fitted) background!"
                    raise IntegrityCheckError(msg)
