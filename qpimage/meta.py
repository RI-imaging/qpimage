DATA_KEYS = ["medium index",  # refractive index of the medium
             "pixel size",  # detector pixel size [m]
             "time",  # acquisition time of the image (float)
             "wavelength",  # imaging wavelength [m]
             ]

OTHER_KEYS = ["dm exclude",  # DryMass: exclude image from  analysis
              "sim center",  # Simulation: center of object [px]
              "sim index",  # Simulation: refractive index of object
              "sim radius",  # Simulation: object radius [m]
              "identifier",  # image identifier
              "qpimage version",  # software version used
              ]

META_KEYS = DATA_KEYS + OTHER_KEYS


class MetaDataMissingError(BaseException):
    pass


class MetaDict(dict):
    """A dictionary containing meta data variables

    Valid keynames are combined in the
    :py:const:`qpimage.meta.META_KEYS` variable.

    Methods
    -------
    __setitem__
    """

    def __init__(self, *args, **kwargs):
        super(MetaDict, self).__init__(*args, **kwargs)
        for key in self:
            if key not in META_KEYS:
                raise KeyError("Unknown meta variable: '{}'".format(key))

    def __setitem__(self, key, value):
        """Set a meta data variable

        The key must be a valid key defined in the
        :py:const:`qpimage.meta.META_KEYS` variable.
        """
        if key not in META_KEYS:
            raise KeyError("Unknown meta variable: '{}'".format(key))
        super(MetaDict, self).__setitem__(key, value)

    def __getitem__(self, *args, **kwargs):
        if args[0] not in self:
            msg = "No meta data was defined for '{}'! ".format(args[0]) \
                  + "Please make sure you passed the dictionary `meta_data` " \
                  + "when creating the QPImage instance."
            raise MetaDataMissingError(msg)
        return super(MetaDict, self).__getitem__(*args, **kwargs)
