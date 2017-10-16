VALID_META_KEYS = ["medium index",
                   "pixel size",
                   "time",
                   "wavelength",
                   ]

OTHER_META_KEYS = ["qpimage version",
                   ]

META_KEYS = VALID_META_KEYS + OTHER_META_KEYS


class MetaDataMissingError(BaseException):
    pass


class MetaDict(dict):
    """A dictionary containing meta data variables

    Valid keynames are given in the
    :py:const:`qpimage.meta.VALID_META_KEYS` variable.

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
        :py:const:`qpimage.meta.VALID_META_KEYS` variable.
        """
        if key not in META_KEYS:
            raise KeyError("Unknown meta variable: '{}'".format(key))
        super(MetaDict, self).__setitem__(key, value)

    def __getitem__(self, *args, **kwargs):
        if args[0] not in self:
            msg = "No meta data was defined for {}! ".format(args[0]) \
                  + "Please make sure you passed the dictionary `meta_data` " \
                  + "when creating the QPImage instance."
            raise MetaDataMissingError(msg)
        return super(MetaDict, self).__getitem__(*args, **kwargs)
