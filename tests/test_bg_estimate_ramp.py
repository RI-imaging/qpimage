import pathlib

import qpimage.integrity_check


def test_ramp_from_h5file():
    """"
    The data for this test was created using:


    ```
    import numpy as np
    import qpimage

    size = 50
    # background phase image with a ramp
    bg = np.repeat(np.linspace(0, 1, size), size).reshape(size, size)
    bg = .6 * bg - .8 * bg.transpose() + .2
    # phase image with random noise
    rsobj = np.random.RandomState(47)
    phase = rsobj.rand(size, size) - .5 + bg

    # create QPImage instance
    with qpimage.QPImage(data=phase,
                         which_data="phase",
                         h5file="bg_ramp.h5") as qpi:
        qpi.compute_bg(which_data="phase",  # correct phase image
                       fit_offset="fit",  # use bg offset from ramp fit
                       fit_profile="ramp",  # perform 2D ramp fit
                       border_px=5,  # use 5 px border around image
                       )
    ```
    """
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpimage.integrity_check.check(h5file, checks=["background"])


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
