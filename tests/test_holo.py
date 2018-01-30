import numpy as np

import qpimage


def hologram(size=64):
    x = np.arange(size).reshape(-1, 1) - size / 2
    y = np.arange(size).reshape(1, -1) - size / 2

    amp = np.linspace(.9, 1.1, size * size).reshape(size, size)
    pha = np.linspace(0, 2, size * size).reshape(size, size)

    rad = x**2 + y**2 > (size / 3)**2
    pha[rad] = 0
    amp[rad] = 1

    # frequencies must match pixel in Fourier space
    kx = 2 * np.pi * -.3
    ky = 2 * np.pi * -.3
    image = (amp**2 + np.sin(kx * x + ky * y + pha) + 1) * 255
    return image


def test_find_sideband():
    size = 40
    ft_data = np.zeros((size, size))
    fx = np.fft.fftshift(np.fft.fftfreq(size))
    ft_data[2, 3] = 1
    ft_data[-3, -2] = 1

    sb1 = qpimage.holo.find_sideband(ft_data=ft_data,
                                     which=+1)
    assert np.allclose(sb1, (fx[2], fx[3]))

    sb2 = qpimage.holo.find_sideband(ft_data=ft_data,
                                     which=-1)
    assert np.allclose(sb2, (fx[-3], fx[-2]))


def test_find_sideband_error():
    size = 40
    ft_data = np.zeros((size, size))
    ft_data[2, 3] = 1
    ft_data[-3, -2] = 1

    try:
        qpimage.holo.find_sideband(ft_data=ft_data,
                                   which=2)
    except ValueError:
        pass
    else:
        assert False, "2 is not a sideband"


def test_fourier2dpad():
    data = np.zeros((100, 120))
    fft1 = qpimage.holo.fourier2dpad(data, zero_pad=True)
    assert fft1.shape == (256, 256)

    fft2 = qpimage.holo.fourier2dpad(data, zero_pad=False)
    assert fft2.shape == data.shape


def test_get_field_error():
    holo = hologram()

    try:
        qpimage.holo.get_field(hologram=holo, filter_size=2)
    except ValueError:
        pass
    else:
        assert False, "filter_size<1 is distance b/w sideband and center"


def test_get_field_filter_names():
    holo = hologram()

    kwargs = dict(hologram=holo,
                  sideband=+1,
                  filter_size=1 / 3,
                  subtract_mean=True,
                  zero_pad=True)

    r_disk = qpimage.holo.get_field(filter_name="disk", **kwargs)
    assert np.allclose(
        r_disk[32, 32], 97.307780444912936 - 76.397860381241372j)

    r_smooth_disk = qpimage.holo.get_field(filter_name="smooth disk", **kwargs)
    assert np.allclose(r_smooth_disk[32, 32],
                       108.36665064909741 - 67.176090709644185j)

    r_gauss = qpimage.holo.get_field(filter_name="gauss", **kwargs)
    assert np.allclose(
        r_gauss[32, 32], 108.26984751082375 - 67.116410573093304j)

    r_square = qpimage.holo.get_field(filter_name="square", **kwargs)
    assert np.allclose(
        r_square[32, 32], 102.3285348843612 - 74.139058665601155j)

    r_smsquare = qpimage.holo.get_field(filter_name="smooth square", **kwargs)
    assert np.allclose(
        r_smsquare[32, 32], 105.23157221309754 - 70.593282942004862j)

    r_tukey = qpimage.holo.get_field(filter_name="tukey", **kwargs)
    assert np.allclose(
        r_tukey[32, 32], 113.4826495540899 - 59.546232775481869j)

    try:
        qpimage.holo.get_field(filter_name="unknown", **kwargs)
    except ValueError:
        pass
    else:
        assert False, "unknown filter accepted"


def test_get_field_int_copy():
    holo = hologram()
    holo = np.array(holo, dtype=int)

    kwargs = dict(sideband=+1,
                  filter_size=1 / 3,
                  subtract_mean=True,
                  zero_pad=True)

    res1 = qpimage.holo.get_field(hologram=holo,
                                  copy=False,
                                  **kwargs)
    res2 = qpimage.holo.get_field(hologram=holo,
                                  copy=True,
                                  **kwargs)
    res3 = qpimage.holo.get_field(hologram=holo.astype(float),
                                  copy=True,
                                  **kwargs)
    assert np.all(res1 == res2)
    assert np.all(res1 == res3)


def test_get_field_sideband():
    holo = hologram()

    ft_data = qpimage.holo.fourier2dpad(data=holo, zero_pad=True)
    sideband = qpimage.holo.find_sideband(ft_data, which=+1, copy=True)

    kwargs = dict(hologram=holo,
                  filter_name="disk",
                  filter_size=1 / 3,
                  subtract_mean=True,
                  zero_pad=True)
    res1 = qpimage.holo.get_field(sideband=+1, **kwargs)
    res2 = qpimage.holo.get_field(sideband=sideband, **kwargs)
    assert np.all(res1 == res2)


def test_qpimage_holo():
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
                          which_data="hologram",
                          holo_kw={"filter_name": "gauss"})
    qpi.compute_bg(which_data="phase",
                   fit_offset="fit",
                   fit_profile="tilt",
                   border_px=5)
    assert np.allclose(disk_max, qpi.pha.max(), rtol=.01, atol=0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
