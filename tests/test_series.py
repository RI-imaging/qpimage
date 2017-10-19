from os.path import abspath, dirname, join
import sys
import tempfile

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpimage  # noqa: E402


def test_series_from_list():
    h5file = join(dirname(abspath(__file__)), "data/bg_ramp.h5")
    qpi1 = qpimage.QPImage(h5file=h5file)
    qpi2 = qpi1.copy()

    qps = qpimage.QPSeries(qpimage_list=[qpi1, qpi2])
    assert len(qps) == 2
    assert qps.get_qpimage(0) == qps.get_qpimage(1)


def test_series_h5file():
    h5file = join(dirname(abspath(__file__)), "data/bg_ramp.h5")
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


def test_series_error_meta():
    h5file = join(dirname(abspath(__file__)), "data/bg_ramp.h5")
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


def test_series_error_key():
    h5file = join(dirname(abspath(__file__)), "data/bg_ramp.h5")
    qpi1 = qpimage.QPImage(h5file=h5file)
    qpi2 = qpi1.copy()

    qps = qpimage.QPSeries(qpimage_list=[qpi1, qpi2])
    try:
        qps.get_qpimage(2)
    except KeyError:
        pass
    else:
        assert False, "get index 2 when length is 2"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
