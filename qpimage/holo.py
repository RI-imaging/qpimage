import numpy as np


def find_sideband(data):
    """Find the side band position of a hologram

    The hologram is Fourier-transformed and the side band
    is determined by finding the maximum amplitude in
    Fourier space.

    Parameters
    ----------
    data : 2d ndarray
        hologram image


    Returns
    -------
    sb_loc : tuple of floats
        (x,y) coordinates of the side band in Fourier space
        measured from the center in the shifted Fourier transform.
    """
    # fourier transform
    fft = fourier2dpad(data)

    # Zero padded (larger)
    order = len(fft)

    # remove lower part
    minlo = max(int(np.ceil(order / 42)), 5)
    fft[order // 2 - minlo:] = 0
    # remove axis part
    center = int(order / 2)
    fft[center - 3:center + 3, :] = 0
    fft[:, center - 3:center + 3] = 0

    am = np.argmax(np.abs(fft))
    y = am % order
    x = (am - y) / order

    diskrad = int(order / 23)

    xv = np.arange(order).reshape(-1, 1)
    yv = xv.reshape(1, -1)

    fft[np.where((xv - x)**2 + (yv - y)**2 > diskrad**2)] = 0

    return (int(x - order / 2), int(y - order / 2))


def fourier2dpad(data):
    """Compute the 2D Fourier transform with zero padding"""
    # Zero padding to square image
    (N, M) = data.shape

    # zero padding
    order = np.int(max(64., 2**np.ceil(np.log(2 * max(N, M)) / np.log(2))))
    datapad = np.pad(data, ((0, order - N), (0, order - M)), mode="constant")

    # fourier transform
    fft = np.fft.fftshift(np.fft.fft2(datapad))

    return fft


def get_field(data, sb_loc=None, filt_size=None, filt_type="gauss"):
    """Computes phase and amplitude from a holographic image

    Parameters
    ----------
    data : 2d ndarray
        Hologram data
    sb_loc : tuple of floats (x0,y0)
        Coordinates of the side band in Fourier space.
    filt_size : float
        Radius of the filter in Fourier space in px.
        If set to None, the radius will be estimated using `sb_loc`.
    filt_type : float
        One of {"disk", "gauss"}

    x0 and y0 are center of the filter
    R is factor for "radius" of filter (sqrt(x0² + y0²)/np.pi)

    filter_type can be "disk" or "gauss"

    Notes
    -----
    `sb_loc` are in FT of zero-padded image, see :func:`fourier2dpad`.
    """
    if sb_loc is None:
        sb_loc = find_sideband(data)

    x0, y0 = sb_loc
    n, m = data.shape

    # fourier transform
    fft = fourier2dpad(data)

    # Zero padded (larger)
    order = len(fft)

    center = order / 2 - .5
    x = np.linspace(-center, center, order, endpoint=False)
    xv = x.reshape(-1, 1)
    yv = x.reshape(1, -1)

    if filt_size is None:
        # Estimate filter size based on the distance to the origin
        filt_size = int(np.ceil(min(np.abs(sb_loc) / 2)))

    if filt_type == "gauss":
        # gaussian filter_type
        afilter = np.exp(-((xv - x0)**2 + (yv - y0)**2) / (filt_size**2))
        afilter /= np.max(afilter)
    elif filt_type == "disk":
        # disk fitlering
        afilter = ((xv - x0)**2 + (yv - y0)**2) < filt_size**2
    else:
        print("Unknown filter: {}".format(filt_type))
    # filter here
    fft_filt = afilter * fft

    # Shift image to zero
    shifted = np.roll(np.roll(fft_filt, -x0, axis=0), -y0, axis=1)

    # inverse fourier transform
    field = np.fft.ifft2(np.fft.ifftshift(shifted))[:n, :m]
    return field
