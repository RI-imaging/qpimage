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
        FFt-shifted Fourier transform of the hologram image
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

    return fx, fy


def fourier2dpad(data, zero_pad=True):
    """Compute the FFT-shifted 2D Fourier transform with zero padding

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
        order = int(max(64., 2**np.ceil(np.log(2 * max(N, M)) / np.log(2))))

        # this is faster than np.pad
        datapad = np.zeros((order, order), dtype=float)
        datapad[:data.shape[0], :data.shape[1]] = data
    else:
        datapad = data

    # Fourier transform
    fft = np.fft.fftshift(np.fft.fft2(datapad))
    return fft


def get_field(hologram, sideband=+1, filter_name="disk", filter_size=1/3,
              filter_size_interpretation="sideband distance",
              subtract_mean=True, zero_pad=True, copy=True, ret_mask=False):
    """Compute the complex field from a hologram using Fourier analysis

    Parameters
    ----------
    hologram: real-valued 2d ndarray
        hologram data (if this is a 3d array, then the first slice
        defined by the first two axes is used)
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
        Size of the filter in Fourier space. The interpretation
        of this value depends on `filter_size_interpretation`.
        See `filter_name` for how it is used in filtering.
    filter_size_interpretation: str
        If set to "sideband distance", the filter size is interpreted
        as the relative distance between central band and sideband
        (this is the default). If set to "frequency index", the filter
        size is interpreted as a Fourier frequency index ("pixel size")
        and must be between 0 and `max(hologram.shape)/2`.
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
    ret_mask: bool
        If set to True, return the filter mask used.

    Notes
    -----
    If the input image has three axes, then only the first image
    (defined by the first two axes) is taken (ignore alpha or
    RGB channels).

    The input image is zero-padded as a square image to the next
    order of :math:`2^n`.

    Even though the size of the "gauss" filter approximately matches
    the frequencies of the "disk" filter, it takes into account
    higher frequencies as well and thus suppresses ringing artifacts
    for data that contain jumps in the phase image.
    """
    if len(hologram.shape) == 3:
        # take the first slice (we have alpha or RGB information)
        hologram = hologram[:, :, 0]

    if copy:
        hologram = hologram.astype(dtype=float, copy=True)

    if subtract_mean:
        # remove contributions of the central band
        # (this affects more than one pixel in the FFT
        # because of zero-padding)
        if issubclass(hologram.dtype.type, np.integer):
            hologram = hologram.astype(float)
        hologram -= hologram.mean()

    # Fourier transform
    fft = fourier2dpad(hologram, zero_pad=zero_pad)

    if sideband in [+1, -1]:
        fsx, fsy = find_sideband(fft, which=sideband)
    else:
        fsx, fsy = sideband

    # roll fft such that sideband is located at the image center
    shifted = np.roll(np.roll(fft, -int(fsx * fft.shape[0]), axis=0),
                      -int(fsy * fft.shape[1]), axis=1)

    # coordinates in Fourier space
    assert fft.shape[0] == fft.shape[1]  # square-shaped Fourier domain
    fx = np.fft.fftshift(np.fft.fftfreq(fft.shape[0])).reshape(-1, 1)
    fy = fx.reshape(1, -1)

    if filter_size_interpretation == "sideband distance":
        # filter size based on distance b/w central band and sideband
        if filter_size <= 0 or filter_size >= 1:
            raise ValueError("For sideband distance interpretation, "
                             "`filter_size` must be between 0 and 1; "
                             f"got '{filter_size}'!")
        fsize = np.sqrt(fsx**2 + fsy**2) * filter_size
    elif filter_size_interpretation == "frequency index":
        # filter size given in Fourier index (number of Fourier pixels)
        if filter_size <= 0 or filter_size >= max(hologram.shape)/2:
            raise ValueError("For frequency index interpretation, "
                             "`filter_size` must be between 0 and "
                             f"max(hologram.shape)/2; got '{filter_size}'!")
        # convert to frequencies (compatible with fx and fy)
        fsize = filter_size / fft.shape[0]
    else:
        raise ValueError("Invalid value for `filter_size_interpretation`: "
                         + f"'{filter_size_interpretation}'")

    if filter_name == "disk":
        afilter = (fx**2 + fy**2) <= fsize**2
    elif filter_name == "smooth disk":
        sigma = fsize / 5
        tau = 2 * sigma**2
        radsq = fx**2 + fy**2
        disk = radsq <= fsize**2
        gauss = np.exp(-radsq / tau)
        afilter = signal.convolve(gauss, disk, mode="same")
        afilter /= afilter.max()
    elif filter_name == "gauss":
        sigma = fsize * .6
        tau = 2 * sigma**2
        afilter = np.exp(-(fx**2 + fy**2) / tau)
        afilter /= afilter.max()
    elif filter_name == "square":
        afilter = (np.abs(fx) <= fsize) * (np.abs(fy) <= fsize)
    elif filter_name == "smooth square":
        blur = fsize / 5
        tau = 2 * blur**2
        square = (np.abs(fx) < fsize) * (np.abs(fy) < fsize)
        gauss = np.exp(-(fy**2) / tau) * np.exp(-(fy**2) / tau)
        afilter = signal.convolve(square, gauss, mode="same")
        afilter /= afilter.max()
    elif filter_name == "tukey":
        alpha = 0.1
        rsize = int(min(fx.size, fy.size)*fsize) * 2
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
    # crop to original image shape
    cropped = field[:hologram.shape[0], :hologram.shape[1]]

    if ret_mask:
        # shift mask center to sideband location
        shifted_mask = np.roll(
            np.roll(afilter, int(fsx * fft.shape[0]), axis=0),
            int(fsy * fft.shape[1]), axis=1)
        return cropped, shifted_mask
    else:
        return cropped
