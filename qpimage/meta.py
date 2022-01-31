import collections

#: QPImage attributes required for each dataset
DATA_DEF = {
    "medium index": "refractive index of the medium",
    "pixel size": "detector pixel size [m]",
    "time": "acquisition time of the image [s]",
    "wavelength": "imaging wavelength [m]",
    }

#: Optional QPImage attributes
OTHER_DEF = {
    "angle": "tomographic acquisition angle [rad]",
    "device": "imaging device used",
    "focus": "focus position [m]",
    "identifier": "image identifier",
    "qpimage version": "qpimage software version used",
    "sim center": "simulation: center of object [px]",
    "sim index": "simulation: refractive index of object",
    "sim model": "simulation: model used",
    "sim radius": "simulation: object radius [m]",
    "software": "imaging software used",
    }

DATA_KEYS = sorted(DATA_DEF.keys())

OTHER_KEYS = sorted(OTHER_DEF.keys())

#: valid :class:`qpimage.core.QPImage` meta data keys
META_KEYS = DATA_KEYS + OTHER_KEYS


class MetaDataMissingError(BaseException):
    """Raised when meta data is missing"""
    pass


class MetaDict(collections.UserDict):
    """Management of meta data variables

    Valid key names are defined in :const:`qpimage.meta.META_KEYS`.
    """
    valid_keys = META_KEYS

    def __init__(self, *args, **kwargs):
        super(MetaDict, self).__init__(*args, **kwargs)
        # check for invalid keys
        for key in self:
            if key not in self.valid_keys:
                raise KeyError("Unknown meta key: '{}'".format(key))

    def __setitem__(self, key, value):
        """Set a meta data key

        The key must be a valid key defined in `self.valid_keys`
        (defaults to :const:`qpimage.meta.META_KEYS`).
        """
        if key not in self.valid_keys:
            raise KeyError("Unknown meta key: '{}'".format(key))
        super(MetaDict, self).__setitem__(key, value)

    def __getitem__(self, *args, **kwargs):
        if args[0] not in self and args[0] in self.valid_keys:
            msg = "No meta data was defined for '{}'!".format(args[0]) \
                  + "Please make sure you passed the dictionary `meta_data` " \
                  + "when you loaded your data."
            raise MetaDataMissingError(msg)
        elif args[0] not in self:
            msg = "Unknown meta key: '{}'!".format(args[0])
            raise KeyError(msg)
        return super(MetaDict, self).__getitem__(*args, **kwargs)
