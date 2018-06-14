import pathlib
import tempfile

import numpy as np

import qpimage


def test_h5file_confusion():
    # make up temporary series file
    seriesfile = tempfile.mktemp(suffix=".h5", prefix="test_qpimage_series_")
    try:
        # h5file should be specified with its corresponding parameter
        qpimage.QPSeries(seriesfile)
    except ValueError:
        pass
    else:
        assert False, "h5file must be given as kwarg!"


def test_getitem():
    size = 20
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)

    qpi1 = qpimage.QPImage(data=1.1 * pha,
                           which_data="phase")
    qpi2 = qpimage.QPImage(data=1.2 * pha,
                           which_data="phase")
    qpi3 = qpimage.QPImage(data=1.3 * pha,
                           which_data="phase")

    series = qpimage.QPSeries(qpimage_list=[qpi1, qpi2, qpi3])

    assert qpi1 != qpi2
    assert qpi1 != qpi3
    assert series[0] == qpi1
    assert series[1] == qpi2
    assert series[2] == qpi3
    assert series[-3] == qpi1
    assert series[-2] == qpi2
    assert series[-1] == qpi3

    try:
        series[-4]
    except ValueError:
        pass
    else:
        assert False, "Negative index exceeds size."


def test_getitem_identifier():
    size = 20
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)

    qpi1 = qpimage.QPImage(data=1.1 * pha,
                           which_data="phase",
                           meta_data={"identifier": "peter"})
    qpi2 = qpimage.QPImage(data=1.2 * pha,
                           which_data="phase",
                           meta_data={"identifier": "hans"})
    qpi3 = qpimage.QPImage(data=1.3 * pha,
                           which_data="phase",
                           meta_data={"identifier": "doe"})

    series = qpimage.QPSeries(qpimage_list=[qpi1, qpi2, qpi3])
    assert "peter" in series
    assert "peter_bad" not in series
    assert series["peter"] == qpi1
    assert series["peter"] != qpi2
    assert series["hans"] == qpi2
    assert series["doe"] == qpi3
    try:
        series["john"]
    except KeyError:
        pass
    else:
        assert False, "'john' is not in series"
    try:
        series.add_qpimage(qpi1)
    except ValueError:
        pass
    else:
        assert False, "Adding QPImage with same identifier should not work"


def test_identifier():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_tilt.h5"
    qpi = qpimage.QPImage(h5file=h5file, h5mode="r")
    series1 = qpimage.QPSeries(qpimage_list=[qpi, qpi, qpi],
                               identifier="test_identifier")
    assert series1.identifier == "test_identifier"

    series2 = qpimage.QPSeries(qpimage_list=[qpi, qpi, qpi])
    assert series2.identifier is None


def test_identifier_qpimage():
    size = 20
    pha = np.repeat(np.linspace(0, 10, size), size)
    pha = pha.reshape(size, size)

    qpi1 = qpimage.QPImage(data=1.1 * pha,
                           which_data="phase")
    qpi2 = qpimage.QPImage(data=1.2 * pha,
                           which_data="phase")
    qpi3 = qpimage.QPImage(data=1.3 * pha,
                           which_data="phase")

    series = qpimage.QPSeries(qpimage_list=[qpi1, qpi2])
    series.add_qpimage(qpi=qpi3, identifier="hastalavista")
    assert series[2]["identifier"] == "hastalavista"


def test_iter():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_tilt.h5"
    qpi = qpimage.QPImage(h5file=h5file, h5mode="r")
    series = qpimage.QPSeries(qpimage_list=[qpi, qpi, qpi])

    for qpj in series:
        assert qpj == qpi


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
