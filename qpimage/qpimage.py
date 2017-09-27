import numpy as np
from skimage.restoration import unwrap_phase

from .amplitude import Amplitude
from .phase import Phase


class QPImage(object):
    def __init__(self, data, wavelength, sampling,
                 bg_data=None, data_type="phase,intensity"):
        """Quantitative phase imaging data

        Parameters
        ----------
        data: 2d ndarray (float or complex) or list
            The experimental data (see `data_type`)
        wavelength: float
            Wavelength of the radiation used [m]
        sampling: float
            Pixel size [m]
        bg_data: 2d ndarray (float or complex), list, or `None`
            The background data (must be same type as `data`)
        data_type: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object with
            the phase data as first element.
        """
        # register data_type
        self._data_type = data_type
        # compute phase and amplitude from input data
        self._amp, self._pha = self._get_amp_pha(data, data_type)
        # set backgroudn data
        self.set_bg_data(bg_data)

    def _get_amp_pha(self, data, data_type):
        """Convert input data to phase and amplitude

        Parameters
        ----------
        data: 2d ndarray (float or complex) or list
            The experimental data (see `data_type`)
        data_type: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object with
            the phase data as first element.

        Returns
        -------
        amp, pha: tuple of (:py:class:`Amplitdue`, :py:class:`Phase`)
        """
        assert data_type in ["field", "phase", "phase,amplitude",
                             "phase,intensity"]
        if data_type == "field":
            amp = np.abs(data)
            pha = unwrap_phase(np.angle(data))
        elif data_type == "phase":
            amp = np.ones_like(data)
            pha = unwrap_phase(data)
        elif data_type == "phase,amplitude":
            pha = unwrap_phase(data[0])
            amp = data[1]
        elif data_type == "phase,intensity":
            pha = unwrap_phase(data[0])
            amp = np.sqrt(data[1])
        return Amplitude(amp), Phase(pha)

    @property
    def bg_amp(self):
        """Return the background amplitude image"""
        return self._amp.bg

    @property
    def bg_pha(self):
        """Return the background phase image"""
        return self._pha.bg

    @property
    def amp(self):
        """Return the background-corrected amplitude image"""
        return self._amp.raw / self._amp.bg

    @property
    def field(self):
        """Return the background-corrected complex field"""
        return self.amp * np.exp(1j*self.pha)

    @property
    def pha(self):
        """Return the background-corrected phase image"""
        return self._pha.raw - self._pha.bg

    def correct_amp(self, method="border"):
        """Perform amplitude background correction
        """

    def correct_pha(self, method="border,sphere-edge"):
        """Perform phase background correction
        """

    def refocus(self, distance, method="helmholtz"):
        """Numerically refocus the current field

        Parameters
        ----------
        distance: float
            Focusing distance [m]
        method: str
            Refocusing method, one of ["helmholtz","fresnel"]

        See Also
        --------
        :py:mod:`nrefocus`: library used for numerical focusing
        """

    def set_bg_data(self, bg_data, data_type=None):
        """Set background data

        Parameters
        ----------
        bg_data: 2d ndarray (float or complex), list, or `None`
            The background data (must be same type as `data`).
            If set to `None`, the background data is reset.
        data_type: str
            String or comma-separated list of strings indicating
            the order and type of input data. Valid values are
            "field", "phase", "phase,amplitude", or "phase,intensity",
            where the latter two require an indexable object with
            the phase data as first element. If set to `None`,
            the `data_type` used during initialization is used.
        """
        if data_type is None:
            # Use initial data_type
            data_type = self._data_type
        if bg_data is None:
            # Reset phase and amplitude
            amp, pha = 1, 0
        else:
            # Compute phase and amplitude from data and data_type
            amp, pha = self._get_amp_pha(bg_data, data_type)
        # Set background data
        self._amp.set_bg(amp)
        self._pha.set_bg(pha)
