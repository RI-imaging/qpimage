import pathlib

import numpy as np

import qpimage


def test_contains():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_tilt.h5"
    qpi = qpimage.QPImage(h5file=h5file, h5mode="r")
    assert "wavelength" in qpi
    assert "hans-peter" not in qpi


def test_equals():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_tilt.h5"
    qpi = qpimage.QPImage(h5file=h5file, h5mode="r")

    qpi1 = qpi.copy()
    assert qpi1 == qpi

    qpi1["wavelength"] = 123
    assert qpi1 != qpi

    # change phase data
    qpi2 = qpi.copy()
    qpi2.compute_bg(which_data="phase",
                    fit_offset="mean",
                    fit_profile="offset",
                    border_perc=10)

    # change amplitude data
    qpi3 = qpi.copy()
    qpi3.set_bg_data(bg_data=.01 + qpi3.amp, which_data="field")
    assert qpi3 != qpi


def test_h5file_confusion():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_tilt.h5"
    try:
        # h5file should be specified with its corresponding parameter
        qpimage.QPImage(h5file)
    except ValueError:
        pass
    else:
        assert False, "h5file must be given as kwarg!"


def test_info():
    size = 50
    data = np.zeros((size, size), dtype=float)
    mask = np.zeros_like(data, dtype=bool)
    mask[::2, ::2] = True
    qpi = qpimage.QPImage(data=data,
                          which_data="phase",
                          meta_data={"wavelength": 300e-9,
                                     "pixel size": .12e-6,
                                     })
    # mask with border
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   from_mask=mask,
                   border_px=5)

    info_dict = dict(qpi.info)
    assert 'phase background from mask' in info_dict
    assert 'amplitude background from mask' not in info_dict
    assert info_dict["phase background fit_offset"] == "mean"
    assert info_dict["phase background border_px"] == 5

    qpi.compute_bg(which_data="amplitude",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_px=5)
    info_dict2 = dict(qpi.info)
    assert not info_dict2['amplitude background from mask']


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


def test_setitem():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_tilt.h5"
    qpi = qpimage.QPImage(h5file=h5file, h5mode="r")

    qpi1 = qpi.copy()
    qpi1["pixel size"] = 0.14e-6

    try:
        qpi1["unknown.data"] = "42"
    except KeyError:
        pass
    else:
        assert False, "Unknown meta name sould raise KeyError."


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
