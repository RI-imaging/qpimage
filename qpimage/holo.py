import numpy as np
from scipy import signal


def find_sideband(ft_data, which=+1, copy=True):
    """Find the side band position of a hologram

    The hologram is Fourier-transformed and the side band
    is determined by finding the maximum amplitude in
    Fourier space.

    Parameters
    ----------
    ft_data: 2d ndarray
        Fourier transform of the hologram image
    which: +1 or -1
        which sideband to search for:

        - +1: upper half
        - -1: lower half
    copy: bool
        copy `ft_data` before modification

    Returns
    -------
    fsx, fsy : tuple of floats
        coordinates of the side band in Fourier space frequencies
    """
    if copy:
        ft_data = ft_data.copy()

    if which not in [+1, -1]:
        raise ValueError("`which` must be +1 or -1!")

    ox, oy = ft_data.shape
    cx = ox // 2
    cy = oy // 2

    minlo = max(int(np.ceil(ox / 42)), 5)
    if which == +1:
        # remove lower part
        ft_data[cx - minlo:] = 0
    else:
        ft_data[:cx + minlo] = 0

    # remove values around axes
    ft_data[cx - 3:cx + 3, :] = 0
    ft_data[:, cy - 3:cy + 3] = 0

    # find maximum
    am = np.argmax(np.abs(ft_data))
    iy = am % oy
    ix = int((am - iy) / oy)

    fx = np.fft.fftshift(np.fft.fftfreq(ft_data.shape[0]))[ix]
    fy = np.fft.fftshift(np.fft.fftfreq(ft_data.shape[1]))[iy]

    return (fx, fy)


def fourier2dpad(data, zero_pad=True):
    """Compute the 2D Fourier transform with zero padding

    Parameters
    ----------
    data: 2d fload ndarray
        real-valued image data
    zero_pad: bool
        perform zero-padding to next order of 2
    """
    if zero_pad:
        # zero padding size is next order of 2
        (N, M) = data.shape
        order = np.int(max(64., 2**np.ceil(np.log(2 * max(N, M)) / np.log(2))))

        # this is faster than np.pad
        datapad = np.zeros((order, order), dtype=float)
        datapad[:data.shape[0], :data.shape[1]] = data
    else:
        datapad = data

    # Fourier transform
    fft = np.fft.fftshift(np.fft.fft2(datapad))
    return fft


def get_field(hologram, sideband=+1, filter_name="disk", filter_size=1 / 3,
              subtract_mean=True, zero_pad=True, copy=True):
    """Compute the complex field from a hologram using Fourier analysis

    Parameters
    ----------
    hologram: real-valued 2d ndarray
        hologram data
    sideband: +1, -1, or tuple of (float, float)
        specifies the location of the sideband:

        - +1: sideband in the upper half in Fourier space,
          exact location is found automatically
        - -1: sideband in the lower half in Fourier space,
          exact location is found automatically
        - (float, float): sideband coordinates in
          frequencies in interval [1/"axes size", .5]
    filter_name: str
        specifies the filter to use, one of

        - "disk": binary disk with radius `filter_size`
        - "smooth disk": disk with radius `filter_size` convolved
          with a radial gaussian (`sigma=filter_size/5`)
        - "gauss": radial gaussian (`sigma=0.6*filter_size`)
        - "square": binary square with side length `filter_size`
        - "smooth square": square with side length `filter_size`
          convolved with square gaussian (`sigma=filter_size/5`)
        - "tukey": a square tukey window of width `2*filter_size` and
          `alpha=0.1`
    filter_size: float
        Size of the filter in Fourier space in fractions of the
        distance between central band and sideband.
        See `filter_shape` for interpretation of `filter_size`.
    subtract_mean: bool
        If True, remove the mean of the hologram before performing
        the Fourier transform. This setting is recommended as it
        can reduce artifacts from frequencies around the central
        band.
    zero_pad: bool
        Perform zero-padding before applying the FFT. Setting
        `zero_pad` to `False` increases speed but might
        introduce image distortions such as tilts in the phase
        and amplitude data or dark borders in the amplitude data.
    copy: bool
        If set to True, input `data` is not edited.

    x0 and y0 are center of the filter
    R is factor for "radius" of filter (sqrt(x0² + y0²)/np.pi)

    filter_type can be "disk" or "gauss"

    Notes
    -----
    Even though the size of the "gauss" filter approximately matches
    the frequencies of the "disk" filter, it takes into account
    higher frequencies as well and thus suppresses ringing artifacts
    for data that contain jumps in the phase image.
    """
    if copy:
        hologram = hologram.astype(dtype=np.float, copy=True)

    if subtract_mean:
        # remove contributions of the central band
        # (this affects more than one pixel in the FFT
        # because of zero-padding)
        if issubclass(hologram.dtype.type, np.integer):
            hologram = hologram.astype(np.float)
        hologram -= hologram.mean()

    # Fourier transform
    fft = fourier2dpad(hologram, zero_pad=zero_pad)

    if sideband in [+1, -1]:
        fsx, fsy = find_sideband(fft, which=sideband)
    else:
        fsx, fsy = sideband

    # shift fft to sideband location
    shifted = np.roll(np.roll(fft, -int(fsx * fft.shape[0]), axis=0),
                      -int(fsy * fft.shape[1]), axis=1)

    # coordinates in Fourier space
    fx = np.fft.fftshift(np.fft.fftfreq(fft.shape[0])).reshape(-1, 1)
    fy = np.fft.fftshift(np.fft.fftfreq(fft.shape[1])).reshape(1, -1)

    # filter size based on central band - sideband - distance
    if filter_size >= 1:
        raise ValueError("`filter_size` must be < 1!")
    fsize = np.sqrt(fsx**2 + fsy**2) * filter_size

    if filter_name == "disk":
        afilter = (fx**2 + fy**2) < fsize**2
    elif filter_name == "smooth disk":
        sigma = fsize / 5
        tau = 2 * sigma**2
        radsq = fx**2 + fy**2
        disk = radsq < fsize**2
        gauss = np.exp(-radsq / tau)
        afilter = signal.convolve(gauss, disk, mode="same")
        afilter /= afilter.max()
    elif filter_name == "gauss":
        sigma = fsize * .6
        tau = 2 * sigma**2
        afilter = np.exp(-(fx**2 + fy**2) / tau)
        afilter /= afilter.max()
    elif filter_name == "square":
        afilter = (np.abs(fx) < fsize) * (np.abs(fy) < fsize)
    elif filter_name == "smooth square":
        blur = fsize / 5
        tau = 2 * blur**2
        square = (np.abs(fx) < fsize) * (np.abs(fy) < fsize)
        gauss = np.exp(-(fy**2) / tau) * np.exp(-(fy**2) / tau)
        afilter = signal.convolve(square, gauss, mode="same")
        afilter /= afilter.max()
    elif filter_name == "tukey":
        alpha = 0.1
        rsize = np.int(min(fx.size, fy.size)*fsize) * 2
        tukey_window_x = signal.tukey(rsize, alpha=alpha).reshape(-1, 1)
        tukey_window_y = signal.tukey(rsize, alpha=alpha).reshape(1, -1)
        tukey = tukey_window_x * tukey_window_y
        afilter = np.zeros(shifted.shape)
        s1 = (np.array(shifted.shape) - rsize)//2
        s2 = (np.array(shifted.shape) + rsize)//2
        afilter[s1[0]:s2[0], s1[1]:s2[1]] = tukey
    else:
        raise ValueError("Unknown filter: {}".format(filter_name))

    # apply filter
    fft_filt = afilter * shifted

    # inverse Fourier transform
    field = np.fft.ifft2(np.fft.ifftshift(fft_filt))
    return field[:hologram.shape[0], :hologram.shape[1]]
