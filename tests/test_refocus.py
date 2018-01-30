import numpy as np
import nrefocus
from scipy.ndimage import gaussian_filter

import qpimage


def test_refocus():
    nrkw = {"res": 2,
            "nm": 1,
            "method": "helmholtz",
            "padding": True,
            "d": 5.5}
    meta = {"wavelength": 1e-6,
            "pixel size": 1e-6 / nrkw["res"],
            "medium index": nrkw["nm"]}
    distance = 5.5 * meta["pixel size"]
    size = 40
    x = (np.arange(size) - size / 2).reshape(-1, 1)
    y = (np.arange(size) - size / 2).reshape(1, -1)
    pha = .1
    amp = .5 * (1 + (x**2 + y**2 < size / 3))
    # make smooth to reduce ringing
    amp = gaussian_filter(amp, 1)
    field = amp * np.exp(1j * pha)

    newfield = nrefocus.refocus(field=field, **nrkw)
    qpi0 = qpimage.QPImage(data=newfield,
                           which_data="field",
                           meta_data=meta)
    qpi1 = qpi0.refocus(distance=-distance, method=nrkw["method"])

    # sanity
    assert amp.min() < .51
    assert amp.max() > .99
    assert qpi1.amp.min() < .51
    assert qpi1.amp.max() > .99
    assert np.abs(qpi0.pha).max() > 2 * pha

    # refocusing result
    assert not np.allclose(qpi0.amp, amp, rtol=0, atol=8e-4)
    assert not np.allclose(qpi0.pha, pha, rtol=0, atol=3e-4)
    assert np.allclose(qpi1.amp, amp, rtol=0, atol=8e-4)
    assert np.allclose(qpi1.pha, pha, rtol=0, atol=3e-4)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
