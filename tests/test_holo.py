from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_qpimage_holo():
    # create fake hologram
    size = 200
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    kx = -.6
    ky = -.4
    disk_max = 1.5
    # there is a phase disk as data in the hologram
    data = disk_max * ((x - size / 2)**2 + (y - size / 2)**2 < 30**2)
    image = np.sin(kx * x + ky * y + data)
    qpi = qpimage.QPImage(image, which_data="hologram")
    qpi.compute_bg(which_data="phase",
                   fit_offset="fit",
                   fit_profile="ramp",
                   border_px=5)
    assert np.allclose(disk_max, qpi.pha.max(), rtol=.01, atol=0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
