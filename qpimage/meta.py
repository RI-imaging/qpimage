VALID_META_KEYS = ["pixel_size",
                   "ri_medium",
                   "time",
                   "wavelength",
                   ]


class MetaDict(dict):
    """A dictionary containing meta data variables

    Valid keynames are given in the
    :py:const:`qpimage.meta.VALID_META_KEYS` variable.

    Methods
    -------
    __setitem__
    """

    def __setitem__(self, key, value):
        """Set a meta data variable

        The key must be a valid key defined in the
        :py:const:`qpimage.meta.VALID_META_KEYS` variable.
        """
        if key not in VALID_META_KEYS:
            raise KeyError("Unknown meta variable: '{}'".format(key))
        super(MetaDict, self).__setitem__(key, value)
