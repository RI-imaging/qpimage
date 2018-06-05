import numpy as np

import qpimage


def test_offset_mean_simple():
    size = 200
    bg = 2.5
    rsobj = np.random.RandomState(47)
    data = rsobj.normal(loc=bg, scale=.1, size=(size, size))
    assert np.allclose(np.mean(data), 2.5003227280152887)
    qpi = qpimage.QPImage(data=data, which_data="phase", h5dtype="float64")
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_px=5)
    assert np.allclose(np.mean(qpi.pha), -0.0011984843060164104)


def test_offset_mode_simple():
    size = 200
    bg = 2.5
    rsobj = np.random.RandomState(47)
    data = rsobj.normal(loc=bg, scale=.1, size=(size, size))
    assert np.allclose(np.mean(data), 2.5003227280152887)
    qpi = qpimage.QPImage(data=data, which_data="phase", h5dtype="float64")
    qpi.compute_bg(which_data="phase",
                   fit_offset="mode",
                   fit_profile="offset",
                   border_px=5)
    # Not so good result because of poor statistics
    assert np.allclose(np.mean(qpi.pha), -0.044022731691440088)


def test_offset_gauss_simple():
    size = 200
    bg = 2.5
    rsobj = np.random.RandomState(47)
    data = rsobj.normal(loc=bg, scale=.1, size=(size, size))
    assert np.allclose(np.mean(data), 2.5003227280152887)
    qpi = qpimage.QPImage(data=data, which_data="phase", h5dtype="float64")
    qpi.compute_bg(which_data="phase",
                   fit_offset="gauss",
                   fit_profile="offset",
                   border_px=5)
    # This yields the best results, because the input noise
    # is gaussian.
    assert np.allclose(np.average(qpi.pha), -0.00039833492077054762)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
