import numpy as np

import qpimage
from qpimage import meta
from qpimage import bg_estimate


def test_bg_estimate_errors():
    data = np.zeros((5, 5))

    try:
        bg_estimate.estimate(data, fit_offset="unknown")
    except ValueError:
        pass
    else:
        assert False, "unknown is not a valid key"

    try:
        bg_estimate.estimate(data, fit_profile="unknown")
    except ValueError:
        pass
    else:
        assert False, "unknown is not a valid key"

    try:
        bg_estimate.estimate(data,
                             fit_offset="fit",
                             fit_profile="offset")
    except ValueError:
        pass
    else:
        assert False, "offset cannot be fitted"


def test_mask():
    size = 200
    data = np.zeros((size, size), dtype=float)
    data[size // 2:] = 1
    mask = data == 0
    qpi = qpimage.QPImage(data=data, which_data="phase")
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   from_mask=mask,
                   )
    assert np.allclose(qpi.pha, data)
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   from_mask=~mask,
                   )
    assert np.allclose(qpi.pha, data - 1)


def test_border_m():
    size = 200
    rsobj = np.random.RandomState(47)
    data = rsobj.normal(loc=.4, scale=.1, size=(size, size))
    pixel_size = .1e-6  # 1px = .1µm
    border_px = 5
    border_m = border_px * pixel_size

    qpi = qpimage.QPImage(data=data, which_data="phase")
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_px=5)
    data_px = qpi.pha
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_px=6)
    data_px_false = qpi.pha
    # Make sure different borders yield different results
    assert not np.all(data_px == data_px_false)
    # Make sure QPImage needs the "pixel size" meta data
    try:
        qpi.compute_bg(which_data="phase",
                       fit_offset="mean",
                       fit_profile="offset",
                       border_m=border_m)
    except meta.MetaDataMissingError:
        pass
    else:
        assert False, "meta data required"
    # Create an instance with the correct pixel size
    qpi2 = qpimage.QPImage(data=data, which_data="phase",
                           meta_data={"pixel size": pixel_size})
    qpi2.compute_bg(which_data="phase",
                    fit_offset="mean",
                    fit_profile="offset",
                    border_m=border_m)
    assert np.all(data_px == qpi2.pha)
    # Also test with rounding
    qpi2.compute_bg(which_data="phase",
                    fit_offset="mean",
                    fit_profile="offset",
                    border_m=border_m * 1.05)
    assert np.all(data_px == qpi2.pha)
    qpi2.compute_bg(which_data="phase",
                    fit_offset="mean",
                    fit_profile="offset",
                    border_m=border_m * .95)
    assert np.all(data_px == qpi2.pha)


def test_border_perc():
    size = 200
    rsobj = np.random.RandomState(47)
    data = rsobj.normal(loc=.4, scale=.1, size=(size, size))

    qpi = qpimage.QPImage(data=data, which_data="phase")
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_px=5)
    data_px = qpi.pha
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_perc=2.5)
    assert np.all(qpi.pha == data_px)
    # rounding
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_perc=2.4)
    assert np.all(qpi.pha == data_px)
    qpi.compute_bg(which_data="phase",
                   fit_offset="mean",
                   fit_profile="offset",
                   border_perc=2.1)  # 4px
    assert not np.all(qpi.pha == data_px)


def test_get_mask():
    size = 200
    data = np.zeros((size, size), dtype=float)
    mask = np.zeros_like(data, dtype=bool)
    mask[::2, ::2] = True
    qpi = qpimage.QPImage(data=data, which_data="phase")
    # only mask
    bin1 = qpi.compute_bg(which_data="phase",
                          fit_offset="mean",
                          fit_profile="offset",
                          from_mask=mask,
                          ret_mask=True)
    assert np.all(mask == bin1)
    # mask with border
    bin2 = qpi.compute_bg(which_data="phase",
                          fit_offset="mean",
                          fit_profile="offset",
                          from_mask=mask,
                          border_px=5,
                          ret_mask=True)
    mask2 = mask.copy()
    mask2[5:-5, 5:-5] = False
    assert np.all(mask2 == bin2)


def test_tilt():
    size = 100
    data = np.zeros((size, size))
    data += np.linspace(0, .1, size).reshape(-1, 1)
    bg = bg_estimate.estimate(data=data,
                              fit_offset="fit",
                              fit_profile="tilt",
                              border_px=1)
    assert np.allclose(data, bg)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    keys = sorted(loc.keys())
    for key in keys:
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
