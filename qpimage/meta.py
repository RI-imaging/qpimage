DATA_KEYS = ["medium index",  # refractive index of the medium
             "pixel size",  # detector pixel size [m]
             "time",  # acquisition time of the image (float)
             "wavelength",  # imaging wavelength [m]
             ]

OTHER_KEYS = ["dm exclude",  # DryMass: exclude image from  analysis
              "sim center",  # Simulation: center of object [px]
              "sim index",  # Simulation: refractive index of object
              "sim model",  # Simulation: model used
              "sim radius",  # Simulation: object radius [m]
              "identifier",  # image identifier
              "qpimage version",  # software version used
              ]

#: valid :class:`qpimage.core.QPImage` meta data keys
META_KEYS = DATA_KEYS + OTHER_KEYS


class MetaDataMissingError(BaseException):
    """Raised when meta data is missing"""
    pass


class MetaDict(dict):
    """Management of meta data variables

    Valid key names are combined in the
    :const:`qpimage.meta.META_KEYS` variable.
    """

    def __init__(self, *args, **kwargs):
        super(MetaDict, self).__init__(*args, **kwargs)
        # check for invalid keys
        for key in self:
            if key not in META_KEYS:
                raise KeyError("Unknown meta key: '{}'".format(key))

    def __setitem__(self, key, value):
        """Set a meta data key

        The key must be a valid key defined in the
        :const:`qpimage.meta.META_KEYS` variable.
        """
        if key not in META_KEYS:
            raise KeyError("Unknown meta key: '{}'".format(key))
        super(MetaDict, self).__setitem__(key, value)

    def __getitem__(self, *args, **kwargs):
        if args[0] not in self and args[0] in META_KEYS:
            msg = "No meta data was defined for '{}'! ".format(args[0]) \
                  + "Please make sure you passed the dictionary `meta_data` " \
                  + "when creating the QPImage instance."
            raise MetaDataMissingError(msg)
        elif args[0] not in self:
            msg = "Unknown meta key: '{}'!".format(args[0])
            raise KeyError(msg)
        return super(MetaDict, self).__getitem__(*args, **kwargs)
