from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_phase_array():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    qpi = qpimage.QPImage(phase,
                          wavelength=550e-9,
                          sampling=.1e-6,
                          data_type="phase",
                          )
    assert np.all(qpi.pha == phase)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
