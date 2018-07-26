import numpy as np

import qpimage


def test_poly2o():
    """simple 2nd order polynomial test
    """
    size = 40
    mx = .5
    my = -.3
    mxy = .1
    ax = -.05
    ay = .04
    x = np.linspace(-10, 10, size).reshape(-1, 1)
    y = np.linspace(-10, 10, size).reshape(1, -1)
    off = 1

    phase = off \
        + ax * x ** 2 \
        + ay * y ** 2 \
        + mx * x \
        + my * y \
        + mxy * x * y

    qpi = qpimage.QPImage(data=phase, which_data="phase", h5dtype="float64")
    qpi.compute_bg(which_data="phase",
                   fit_profile="poly2o",
                   from_mask=np.ones_like(phase, dtype=bool))

    assert not np.allclose(phase, 0, atol=1e-14, rtol=0)
    assert np.allclose(qpi.pha, 0, atol=1e-14, rtol=0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
