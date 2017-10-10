from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_clear_bg():
    size = 50
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)
    amp = np.linspace(.95, 1.05, size**2).reshape(size, size)

    bg_amp = np.linspace(.93, 1.02, size**2).reshape(size, size)
    bg_pha = pha * .5

    qpi = qpimage.QPImage(data=(pha, amp),
                          bg_data=(bg_pha, bg_amp),
                          which_data="phase,amplitude")
    # amplitude
    assert np.all(qpi.bg_amp == bg_amp)
    qpi.clear_bg(which_data="amplitude", keys="data")
    assert np.allclose(qpi.bg_amp, 1)
    qpi.compute_bg(which_data="amplitude",
                   fit_offset="fit",
                   fit_profile="ramp",
                   border_px=5)
    assert not np.allclose(qpi.bg_amp, 1)
    qpi.clear_bg(which_data="amplitude", keys="fit")
    assert np.allclose(qpi.bg_amp, 1)
    # phase
    assert np.all(qpi.bg_pha == bg_pha)
    qpi.clear_bg(which_data="phase", keys="data")


def test_clear_bg_error():
    size = 50
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)
    qpi = qpimage.QPImage(pha, which_data="phase")
    try:
        qpi.clear_bg(which_data="gretel")
    except ValueError:
        pass
    else:
        assert False, "clear bg of invalid which_data should not work"


def test_comput_bg_error():
    size = 50
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)
    qpi = qpimage.QPImage(pha, which_data="phase",
                          meta_data={"pixel size": .1})
    try:
        qpi.compute_bg(which_data="hänsel", border_px=4)
    except ValueError:
        pass
    else:
        assert False, "invalid which_data used for compute_bg"
    try:
        qpi.compute_bg(which_data="phase")
    except ValueError:
        pass
    else:
        assert False, "computation of bg from undefined binary"
    try:
        qpi.compute_bg(which_data="phase", border_m=-1)
    except ValueError:
        pass
    else:
        assert False, "negative border not allowed"
    try:
        qpi.compute_bg(which_data="phase", border_perc=60)
    except ValueError:
        pass
    else:
        assert False, "more than 50 percent border not allowed"
    try:
        qpi.compute_bg(which_data="phase", border_perc=-10)
    except ValueError:
        pass
    else:
        assert False, "negative percent border not allowed"


def test_get_amp_pha():
    # make sure no errors when printing repr
    size = 50
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)
    amp = np.linspace(.95, 1.05, size**2).reshape(size, size)
    field = amp * np.exp(1j * pha)
    inten = amp**2

    qpi1 = qpimage.QPImage(pha, which_data="phase")
    qpi2 = qpimage.QPImage([pha, amp], which_data="phase,amplitude")
    qpi3 = qpimage.QPImage([pha, inten], which_data="phase,intensity")
    qpi4 = qpimage.QPImage(field, which_data="field")

    # test phases
    assert np.allclose(qpi1.pha, qpi2.pha)
    assert np.allclose(qpi1.pha, qpi3.pha)
    assert np.allclose(qpi1.pha, qpi4.pha)

    # test amplitudes
    assert np.allclose(qpi1.amp, 1)
    assert np.allclose(qpi2.amp, qpi3.amp)
    assert np.allclose(qpi2.amp, qpi4.amp)


def test_get_amp_pha_invalid():
    size = 50
    data = np.zeros((size, size))
    try:
        qpimage.QPImage(data, which_data="jean-luc")
    except ValueError:
        pass
    else:
        assert False, "invalid which_data should not work"


def test_get_amp_pha_holo():
    # create fake hologram
    size = 200
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    kx = -.6
    ky = -.4
    image = np.sin(kx * x + ky * y)
    qpi = qpimage.QPImage(image, which_data="hologram")
    qpi.compute_bg(which_data="phase",
                   fit_offset="fit",
                   fit_profile="ramp",
                   border_px=5)
    assert np.abs(qpi.pha).max() < .1


def test_properties():
    size = 50
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)
    amp = np.linspace(.95, 1.05, size**2).reshape(size, size)

    bg_amp = np.linspace(.93, 1.02, size**2).reshape(size, size)
    bg_pha = pha * .5

    qpi = qpimage.QPImage((pha, amp), bg_data=(bg_pha, bg_amp),
                          which_data="phase,amplitude")

    assert np.all(qpi.bg_amp == bg_amp)
    assert np.all(qpi.bg_pha == bg_pha)

    assert np.iscomplexobj(qpi.field)
    fval = -0.46418608511978926 + 0.91376822116221712j
    assert np.allclose(qpi.field[20, 20], fval)

    assert qpi.shape == (size, size)

    qpi.compute_bg(which_data=["phase", "amplitude"],
                   fit_offset="fit",
                   fit_profile="ramp",
                   border_px=5)

    assert not np.all(qpi.bg_amp == bg_amp)
    assert not np.all(qpi.bg_pha == bg_pha)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
