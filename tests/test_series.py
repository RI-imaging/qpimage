import os
import pathlib
import tempfile

import h5py

import qpimage


def test_series_h5file():
    tf = tempfile.mktemp(suffix=".h5", prefix="qpimage_test_")
    with h5py.File(tf, mode="a") as fd:
        qps = qpimage.QPSeries(h5file=fd)
        assert len(qps) == 0
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_series_from_list():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpi1 = qpimage.QPImage(h5file=h5file)
    qpi2 = qpi1.copy()

    qps = qpimage.QPSeries(qpimage_list=[qpi1, qpi2])
    assert len(qps) == 2
    assert qps.get_qpimage(0) == qps.get_qpimage(1)


def test_series_from_h5file():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpi1 = qpimage.QPImage(h5file=h5file)
    qpi2 = qpi1.copy()

    tf = tempfile.mktemp(suffix=".h5", prefix="qpimage_test_")
    with qpimage.QPSeries(qpimage_list=[qpi1, qpi2],
                          h5file=tf,
                          h5mode="a"
                          ):
        pass

    qps2 = qpimage.QPSeries(h5file=tf, h5mode="r")
    assert len(qps2) == 2
    assert qps2.get_qpimage(0) == qpi1
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_series_meta():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpi1 = qpimage.QPImage(h5file=h5file, meta_data={"wavelength": 300e-9})
    assert qpi1.meta["wavelength"] == 300e-9
    qps = qpimage.QPSeries(qpimage_list=[qpi1], meta_data={
                           "wavelength": 400e-9})
    assert qps.get_qpimage(0).meta["wavelength"] == 400e-9


def test_series_error_meta():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpi1 = qpimage.QPImage(h5file=h5file)
    qpi2 = qpi1.copy()

    tf = tempfile.mktemp(suffix=".h5", prefix="qpimage_test_")
    with qpimage.QPSeries(qpimage_list=[qpi1, qpi2],
                          h5file=tf,
                          h5mode="a"
                          ):
        pass

    try:
        qpimage.QPSeries(h5file=tf, h5mode="r",
                         meta_data={"wavelength": 550e-9})
    except ValueError:
        pass
    else:
        assert False, "`meta_data` and `h5mode=='r'`"
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_series_error_key():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpi1 = qpimage.QPImage(h5file=h5file)
    qpi2 = qpi1.copy()

    qps = qpimage.QPSeries(qpimage_list=[qpi1, qpi2])
    try:
        qps.get_qpimage(2)
    except KeyError:
        pass
    else:
        assert False, "get index 2 when length is 2"


def test_series_error_file_is_qpimage():
    h5file = pathlib.Path(__file__).parent / "data" / "bg_ramp.h5"
    qpi1 = qpimage.QPImage(h5file=h5file)
    tf = tempfile.mktemp(suffix=".h5", prefix="qpimage_test_")
    with qpi1.copy(h5file=tf):
        pass

    try:
        qpimage.QPSeries(qpimage_list=[qpi1], h5file=tf)
    except ValueError:
        pass
    else:
        assert False, "tf is a qpimage file"
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_series_error_noqpimage():
    try:
        qpimage.QPSeries(qpimage_list=["hans", 1])
    except ValueError:
        pass
    else:
        assert False, "qpimage list must contain QPImages"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
