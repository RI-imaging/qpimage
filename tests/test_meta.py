import qpimage
import qpimage.meta


def test_meta():
    mm = qpimage.meta.MetaDict()
    mm["wavelength"] = 100e-9
    assert mm["wavelength"] == 100e-9


def test_meta_error():
    mm = qpimage.meta.MetaDict()
    try:
        mm["peter"] = "hans"
    except KeyError:
        pass
    else:
        assert False, "invalid key 'peter' should not work!"

    try:
        qpimage.meta.MetaDict({"peter2": "hans2"})
    except KeyError:
        pass
    else:
        assert False, "invalid key 'peter2' should not work!"

    try:
        mm["peter"]
    except KeyError:
        pass
    else:
        assert False, "invalid key 'peter' should raise KeyError!"

    try:
        mm["medium index"]
    except qpimage.meta.MetaDataMissingError:
        pass
    else:
        assert False, "valid key undefined should raise MetaDataMissingError"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
