from os.path import abspath, dirname, join
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_copy():
    h5file = join(dirname(abspath(__file__)), "data/bg_ramp.h5")
    qpi = qpimage.QPImage(h5file=h5file)
    # create an in-memory copy
    qpi2 = qpi.copy()
    assert np.allclose(qpi.pha, qpi2.pha)
    assert qpi.meta == qpi2.meta


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
