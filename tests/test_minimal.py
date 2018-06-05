import os
import tempfile

import numpy as np

import qpimage


def test_phase_array():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    with qpimage.QPImage(phase, which_data="phase", h5dtype="float64") as qpi:
        assert np.all(qpi.pha == phase)


def test_file():
    h5file = tempfile.mktemp(suffix=".h5", prefix="qpimage_test_")
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    # Write data to disk
    with qpimage.QPImage(phase,
                         which_data="phase",
                         h5file=h5file,
                         h5mode="a",
                         ) as qpi:
        p1 = qpi.pha
        a1 = qpi.amp
    # Open data read-only
    qpi2 = qpimage.QPImage(h5file=h5file, h5mode="r")
    assert np.all(p1 == qpi2.pha)
    assert np.all(a1 == qpi2.amp)
    # cleanup
    try:
        os.remove(h5file)
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
