import warnings

import numpy as np

import qpimage
import qpimage.image_data


def test_bad_keys_error():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    clspha = qpi._pha
    try:
        clspha.del_bg("peter")
    except ValueError:
        pass
    else:
        assert False

    try:
        clspha.get_bg("peter")
    except ValueError:
        pass
    else:
        assert False

    try:
        clspha.set_bg(bg=None, key="peter")
    except ValueError:
        pass
    else:
        assert False


def test_del_warning():
    size = 50
    data = np.zeros((size, size), dtype=float)
    qpi = qpimage.QPImage(data=data,
                          which_data="phase",
                          )
    clspha = qpi._pha
    with warnings.catch_warnings(record=True) as rw:
        clspha.del_bg("data")
        assert len(rw) == 1
        msg = str(rw[0].message)
        assert msg.count("data")
        assert msg.lower().count("no bg data")


def test_get_bg():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    bgpha = qpi.bg_pha
    clspha = qpi._pha
    assert np.all(bgpha == clspha.bg)
    assert np.all(bgpha == clspha.get_bg(key=None))


def test_get_bg_error():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    clspha = qpi._pha
    try:
        clspha.get_bg(key=None, ret_attrs=True)
    except ValueError:
        pass
    else:
        assert False, "attrs of combined bg not supported"


def test_set_bg():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    pha = qpi.pha
    clspha = qpi._pha
    assert np.all(pha == clspha.image)
    clspha.set_bg(None, key="data")
    assert not np.all(pha == clspha.image)


def test_set_bg_error():
    size = 200
    phase = np.repeat(np.linspace(0, np.pi, size), size)
    phase = phase.reshape(size, size)
    bgphase = np.sqrt(np.abs(phase))

    qpi = qpimage.QPImage(phase, bg_data=bgphase, which_data="phase")
    clspha = qpi._pha
    try:
        clspha.set_bg("bad object", key="data")
    except ValueError:
        pass
    else:
        assert False, "strings cannot be used for bg correction"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
