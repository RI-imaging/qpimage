import os
import tempfile

import h5py
import numpy as np

import qpimage
import qpimage.integrity_check


def test_attributes():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")

    try:
        qpimage.integrity_check.check(qpi, checks="attributes")
    except qpimage.integrity_check.IntegrityCheckError:
        pass
    else:
        assert False, "should raise error, b/c no attributes present"

    qpi2 = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase",
                           meta_data={"medium index": 1.335,
                                      "pixel size": 0.1,
                                      "time": 0.0,
                                      "wavelength": 10e-9,
                                      }
                           )
    qpimage.integrity_check.check(qpi2)


def test_background_mask():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))
    mask = np.zeros_like(bgphase, dtype=bool)
    mask[:10, :] = True
    mask[:, -20] = True
    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    qpi.compute_bg(which_data="phase",
                   fit_offset="fit",
                   fit_profile="tilt",
                   from_mask=mask)
    qpimage.integrity_check.check(qpi, checks="background")


def test_background_fit():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    tf = tempfile.mktemp(suffix=".h5", prefix="qpimage_test_")

    with qpimage.QPImage(phase, which_data="phase", h5file=tf) as qpi:
        qpi.compute_bg(which_data="phase",
                       fit_offset="fit",
                       fit_profile="tilt",
                       border_px=5)

    with h5py.File(tf) as h5:
        h5["phase"]["bg_data"]["fit"][:10] = 9

    try:
        qpimage.integrity_check.check(tf, checks="background")
    except qpimage.integrity_check.IntegrityCheckError:
        pass
    else:
        assert False, "wrong bg saved should not work"
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_wrong_check():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    try:
        qpimage.integrity_check.check(qpi, checks="peter")
    except ValueError:
        pass
    else:
        assert False, "should raise error, b/c check 'peter' undefined"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
