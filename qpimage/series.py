import h5py

from .core import QPImage
from .meta import MetaDict


class QPSeries(object):
    _instances = 0

    def __init__(self, qpimage_list=[], meta_data={},
                 h5file=None, h5mode="a", identifier=None):
        """Quantitative phase image series

        Parameters
        ----------
        qpimage_list: list
            A list of instances of :class:`qpimage.QPImage`.
        meta_data: dict
            Meta data associated with the input data
            (see :class:`qpimage.META_KEYS`). This overrides
            the meta data of the QPImages in `qpimage_list` and, if
            `h5file` is given and `h5mode` is not "r", overrides
            the meta data in `h5file`.
        h5file: str, h5py.Group, h5py.File, or None
            A path to an hdf5 data file where all data is cached. If
            set to `None` (default), all data will be handled in
            memory using the "core" driver of the :mod:`h5py`'s
            :class:`h5py:File` class. If the file does not exist,
            it is created. If the file already exists, it is opened
            with the file mode defined by `hdf5_mode`. If this is
            an instance of h5py.Group or h5py.File, then this will
            be used to internally store all data. If `h5file` is given
            and `qpimage_list` is not empty, all QPImages in
            `qpimage_list` are appended to `h5file` in the given order.
        h5mode: str
            Valid file modes are (only applies if `h5file` is a path):

            - "r": Readonly, file must exist
            - "r+": Read/write, file must exist
            - "w": Create file, truncate if exists
            - "w-" or "x": Create file, fail if exists
            - "a": Read/write if exists, create otherwise (default)
        """
        if qpimage_list and not isinstance(qpimage_list, list):
            msg = "`qpimage_list` must be a list!"
            if isinstance(qpimage_list, str):
                msg += " Did you mean `h5file={}`?".format(qpimage_list)
            raise ValueError(msg)
        if isinstance(h5file, h5py.Group):
            self.h5 = h5file
            self._do_h5_cleanup = False
        else:
            if h5file is None:
                h5kwargs = {"name": "qpseries{}.h5".format(
                    QPSeries._instances),
                    "driver": "core",
                    "backing_store": False,
                    "mode": "a"}
            else:
                h5kwargs = {"name": h5file,
                            "mode": h5mode}
            self.h5 = h5py.File(**h5kwargs)
            self._do_h5_cleanup = True
        QPSeries._instances += 1

        if meta_data and h5mode == "r":
            msg = "`h5mode` must not be 'r' if `meta_data` is given!"
            raise ValueError(msg)

        # make sure self.h5 is not itself a QPImage file
        if "phase" in self.h5 and "amplitude" in self.h5:
            raise ValueError(
                "`h5file` is a QPImage file, not a QPSeries file!")

        # Write QPimage data to h5 file
        for qpi in qpimage_list:
            self.add_qpimage(qpi)

        # Update meta data
        if meta_data:
            meta = MetaDict(meta_data)
            for ii in range(len(self)):
                qpii = self.get_qpimage(index=ii)
                for mk in meta:
                    qpii.h5.attrs[mk] = meta[mk]

        # Set identifier
        if identifier:
            self.h5.attrs["identifier"] = identifier

    def __contains__(self, qpid):
        """test whether a QPImage with the given identifier exists"""
        for ii in range(len(self)):
            qpi = self[ii]
            if "identifier" in qpi and qpi["identifier"] == qpid:
                exists = True
                break
        else:
            exists = False
        return exists

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._do_h5_cleanup:
            self.h5.flush()
            self.h5.close()

    def __getitem__(self, index):
        return self.get_qpimage(index)

    def __iter__(self):
        for ii in range(len(self)):
            yield self[ii]

    def __len__(self):
        keys = list(self.h5.keys())
        keys = [kk for kk in keys if kk.startswith("qpi_")]
        return len(keys)

    @property
    def identifier(self):
        """unique identifier of the series"""
        if "identifier" in self.h5.attrs:
            return self.h5.attrs["identifier"]
        else:
            return None

    def add_qpimage(self, qpi, identifier=None, bg_from_idx=None):
        """Add a QPImage instance to the QPSeries

        Parameters
        ----------
        qpimage: qpimage.QPImage
            The QPImage that is added to the series
        identifier: str
            Identifier key for `qpi`
        bg_from_idx: int or None
            Use the background data from the data stored in this index,
            creating hard links within the hdf5 file.
            (Saves memory if e.g. all qpimages is corrected with the same data)
        """
        if not isinstance(qpi, QPImage):
            raise ValueError("`qpimage` must be instance of QPImage!")
        if "identifier" in qpi and identifier is None:
            identifier = qpi["identifier"]
        if identifier and identifier in self:
            msg = "The identifier '{}' already ".format(identifier) \
                  + "exists! You can either change the identifier of " \
                  + " '{}' or remove it.".format(qpi)
            raise ValueError(msg)
        # determine number of qpimages
        num = len(self)
        # indices start at zero; do not add 1
        name = "qpi_{}".format(num)
        group = self.h5.create_group(name)
        thisqpi = qpi.copy(h5file=group)

        if bg_from_idx is not None:
            # Create hard links
            refqpi = self[bg_from_idx]
            thisqpi._amp.set_bg(bg=refqpi._amp.h5["bg_data"]["data"])
            thisqpi._pha.set_bg(bg=refqpi._pha.h5["bg_data"]["data"])

        if identifier:
            # set identifier
            group.attrs["identifier"] = identifier

    def get_qpimage(self, index):
        """Return a single QPImage of the series

        Parameters
        ----------
        index: int or str
            Index or identifier of the QPImage

        Notes
        -----
        Instead of ``qps.get_qpimage(index)``, it is possible
        to use the short-hand ``qps[index]``.
        """
        if isinstance(index, str):
            # search for the identifier
            for ii in range(len(self)):
                qpi = self[ii]
                if "identifier" in qpi and qpi["identifier"] == index:
                    group = self.h5["qpi_{}".format(ii)]
                    break
            else:
                msg = "QPImage identifier '{}' not found!".format(index)
                raise KeyError(msg)
        else:
            # integer index
            if index < -len(self):
                msg = "Index {} out of bounds for QPSeries of size {}!".format(
                    index, len(self))
                raise ValueError(msg)
            elif index < 0:
                index += len(self)
            name = "qpi_{}".format(index)
            if name in self.h5:
                group = self.h5[name]
            else:
                msg = "Index {} not found for QPSeries of length {}".format(
                    index, len(self))
                raise KeyError(msg)
        return QPImage(h5file=group)
