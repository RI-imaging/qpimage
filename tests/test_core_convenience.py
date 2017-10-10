from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_repr():
    # make sure no errors when printing repr
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    qpi = qpimage.QPImage(phase, which_data="phase",
                          meta_data={"wavelength": 550e-9})
    print(qpi)
    qpi2 = qpimage.QPImage(phase, which_data="phase",
                           meta_data={"wavelength": .1})
    print(qpi2)

    print(qpi._pha)
    print(qpi._amp)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
