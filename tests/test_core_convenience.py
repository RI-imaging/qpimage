from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_info():
    size = 50
    data = np.zeros((size, size), dtype=float)
    binary_mask = np.zeros_like(data, dtype=bool)
    binary_mask[::2, ::2] = True
    qpi = qpimage.QPImage(data=data,
                          which_data="phase",
                          meta_data={"wavelength": 300e-9,
                                     "pixel size": .12e-6,
                                     })
    # binary with border
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   from_binary=binary_mask,
                   border_px=5)

    info_dict = dict(qpi.info)
    assert 'phase background from binary' in info_dict
    assert 'amplitude background from binary' not in info_dict
    assert info_dict["phase background fit_offset"] == "mean"
    assert info_dict["phase background border_px"] == 5

    qpi.compute_bg(which_data="amplitude",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_px=5)
    info_dict2 = dict(qpi.info)
    assert not info_dict2['amplitude background from binary']


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


def test_which_data():
    conv = qpimage.QPImage._conv_which_data
    assert conv("phase") == "phase"
    assert conv("phase,amplitude") == ("phase", "amplitude")
    assert conv("phase, amplitude") == ("phase", "amplitude")
    assert conv("phase,Intensity") == ("phase", "intensity")
    assert conv("Phase") == "phase"
    assert conv("phase,") == "phase"
    assert conv("phase") == "phase"
    assert conv("phase, ") == "phase"
    assert conv(None) is None

    try:
        conv(10)
    except ValueError:
        pass
    else:
        assert False, "which_data can only be list, str, tuple"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
