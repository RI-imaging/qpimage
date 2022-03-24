import numpy as np
import pytest
import qpimage


def test_qpimage_qpretrieve_oah_deprecated():
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
    with pytest.warns(DeprecationWarning, match="qpretrieve_kw"):
        qpi = qpimage.QPImage(image,
                              which_data="raw-oah",
                              holo_kw={"filter_name": "gauss"})
        qpi.compute_bg(which_data="phase",
                       fit_offset="fit",
                       fit_profile="tilt",
                       border_px=5)
    assert np.allclose(disk_max, qpi.pha.max(), rtol=.01, atol=0)


def test_qpimage_qpretrieve_oah():
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
    qpi = qpimage.QPImage(image,
                          which_data="raw-oah",
                          qpretrieve_kw={"filter_name": "gauss"})
    qpi.compute_bg(which_data="phase",
                   fit_offset="fit",
                   fit_profile="tilt",
                   border_px=5)
    assert np.allclose(disk_max, qpi.pha.max(), rtol=.01, atol=0)
