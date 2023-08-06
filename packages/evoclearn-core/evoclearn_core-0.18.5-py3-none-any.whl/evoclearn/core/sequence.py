# -*- coding: utf-8 -*-

import os
import io
import bz2
from glob import glob
from typing import Iterable, Optional
from collections import namedtuple

import numpy as np
import pandas as pd
import xarray as xr
import h5py as h5

from . utils import standard_param_order
from . import log


LOGGER = log.getLogger("evl.core.sequence")


class Sequence(pd.DataFrame):
    """A Dataframe which has a well-defined multi-index and ordered
    columns representing VTL and qTA parameters"""
    IDX_NAMES = ("idx", "lab")

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        assert self.index.names == self.IDX_NAMES
        #assert all(((e, f) for e, f in zip(self.columns, standard_param_order(self.columns))))

    @property
    def _constructor(self):
        return self.__class__

    @classmethod
    def from_json(cls, s: str, dtype=None) -> "Sequence":
        df = pd.read_json(s, orient="table")
        if dtype is not None:
            df = df.astype(dtype, copy=False)
        return cls(df)

    @classmethod
    def from_file(cls, f, dtype=None) -> "Sequence":
        if type(f) is str:
            io_lib = bz2 if f.endswith(".bz2") else io
            with io_lib.open(f, "rt") as infh:
                return cls.from_json(infh.read(), dtype=dtype)
        else:
            return cls.from_json(f.read(), dtype=dtype)

    @classmethod
    def from_xarray(cls, xar: xr.Dataset) -> "Sequence":
        df = xar.to_dataframe()
        mi = map(lambda x: (int(x[0]), x[1]), (l.split("*") for l in df.index))
        df.index = pd.MultiIndex.from_tuples(mi, names=cls.IDX_NAMES)
        return cls(df)

    @classmethod
    def from_spec(cls, params, labels=None, fill_value=np.nan) -> "Sequence":
        assert len(params) == len(set(params))
        labels = labels if labels is not None else ["_"]
        df = pd.DataFrame(fill_value,
                          index=pd.MultiIndex.from_tuples(enumerate(labels), names=cls.IDX_NAMES),
                          columns=standard_param_order(params))
        return cls(df)

    def to_json(self) -> str:
        """No newlines in JSON string"""
        return super(self.__class__, self).to_json(orient="table")

    def to_file(self, f) -> "Sequence":
        if type(f) is str:
            io_lib = bz2 if f.endswith(".bz2") else io
            with io_lib.open(f, "wt") as outfh:
                outfh.write(self.to_json())
        else:
            f.write(self.to_json())
        return self

    def to_xarray(self) -> xr.Dataset:
        df = pd.DataFrame(self).copy()
        df.index = ["*".join(map(str, i)) for i in df.index]
        return df.to_xarray()


ValueColumnsIndex = namedtuple("ValueColumnsIndex", ["values", "columns", "index"])


class Sequences(object):
    IDX_NAMES = ("seqidx",) + Sequence.IDX_NAMES

    def __init__(self,
                 df: pd.DataFrame=None,
                 vci: ValueColumnsIndex=None,
                 xar: xr.Dataset=None,
                 it: Iterable[Sequence]=None):
        """A Sequences instance can be backed by:
        1. An in-memory pd.DataFrame,
        2. An in-memory set of objects (values, columns, index),
        3. An on-disk xr.Dataset (in NetCDF format, could be either a single file or dir)
        4. An iterator yielding Sequence instances

        For the first two cases random access via __getitem__ is implemented
        """
        non_null_args = sum([int(arg is not None) for arg in [df, xar, it, vci]])
        if non_null_args != 1:
            raise Exception("Invalid input to Sequences constructor...")
        if df is not None:
            assert df.index.names == self.IDX_NAMES
            df = df.reindex(sorted(df.index, key=lambda x:x[:2]))
        if vci is not None:
            assert len(vci.values.shape) == 3
        self.vci = vci
        self.df = df
        self._xar = xar
        self._it = it

    def __iter__(self) -> Iterable[Sequence]:
        if self.df is not None:
            return self._df_iter(self.df)
        if self.vci is not None:
            return self._vci_iter()
        elif self._xar is not None:
            return self._xr_iter(self._xar)
        else:
            return self._it

    def __len__(self) -> Optional[int]:
        if self.df is not None:
            return len(set(self.df.index.get_level_values(self.IDX_NAMES[0])))
        elif self.vci is not None:
            return len(self.vci.values)
        elif self._xar is not None:
            return self._xar.dims[self.IDX_NAMES[0]]
        else:
            raise Exception("This instance of Sequences does not support len()...")

    def __getitem__(self, i):
        if not type(i) is int:
            raise TypeError("Only supports integer indices...")
        i = (len(self) + i) if i < 0 else i
        if self.df is not None:
            return Sequence(self.df.loc[i])
        elif self.vci is not None:
            return Sequence(self.vci.values[i],
                            index=pd.MultiIndex.from_tuples(self.vci.index,
                                                            names=Sequence.IDX_NAMES),
                            columns=self.vci.columns)
        elif self._xar is not None:
            df = self._xar.sel({self.IDX_NAMES[0]: i}).to_dataframe()
            return Sequence(Sequences._unpack_multiindex(df))
        else:
            raise Exception("This instance of Sequences does not support random access...")

    @classmethod
    def from_iter(cls,
                  seqs: Iterable[Sequence],
                  slurp: bool=False) -> "Sequences":
        if slurp:
            df = xr.concat((s.to_xarray() for s in seqs),
                           dim=cls.IDX_NAMES[0]).to_dataframe()
            return cls(df=cls._unpack_multiindex(df))
        else:
            return cls(it=seqs)

    @classmethod
    def from_xarray(cls,
                    xar: xr.Dataset,
                    slurp: bool=False) -> "Sequences":
        if slurp:
            xar.load()
            df = xar.to_dataframe()
            return cls(df=cls._unpack_multiindex(df))
        else:
            return cls(xar=xar)

    @classmethod
    def from_netcdf(cls, path: str, slurp: bool=False) -> "Sequences":
        if os.path.isdir(path):
            glb = sorted(glob(os.path.join(path, "*")),
                         key=lambda x:int(os.path.basename(x)))
            xar = xr.open_mfdataset(glb,
                                    combine="nested",
                                    concat_dim=cls.IDX_NAMES[0])
            return cls.from_xarray(xar, slurp)
        else:
            return cls.from_xarray(xr.open_dataset(path), slurp)

    @classmethod
    def from_hdf5(cls, path: str, slurp: bool=False) -> "Sequences":
        if slurp:
            with h5.File(path, "r") as h5f:
                columns = h5f["columns"][:]
                shared_index = h5f["index"][:]
                dset = h5f["values"]
                values = np.zeros_like(dset)
                dset.read_direct(values)
            columns = [col.decode("ascii") for col in columns]
            shared_index = [(int(idx.decode("ascii").split("*")[0]),
                             idx.decode("ascii").split("*")[1]) for idx in shared_index]
            return cls(vci=ValueColumnsIndex(values, columns, shared_index))
        else:
            raise NotImplementedError
        
        
    @classmethod
    def from_disk(cls, path: str, slurp: bool=False) -> "Tracks":
        if path.endswith(".nc"):
            return cls.from_netcdf(path, slurp)
        elif path.endswith(".h5"):
            return cls.from_hdf5(path, slurp)
        else:
            raise NotImplementedError

    @staticmethod
    def df_to_xarray(df) -> xr.Dataset:
        df = df.reindex(sorted(df.index, key=lambda x:x[:2]))
        df.index = ["*".join(map(str, i[1:])) for i in df.index]
        datasets = {}
        segset = None
        for var in df.columns:
            ser = df[var]
            if segset is None:
                segset = sorted(set(ser.index), key=lambda x:int(x.split("*")[0]))
            arr = ser.to_numpy().reshape((-1, len(segset)))
            datasets[var] = xr.DataArray(arr,
                                         dims=[Sequences.IDX_NAMES[0], "index"],
                                         coords={"index": segset})
        xar = xr.Dataset(datasets)
        return xar

    def to_netcdf(self, path: str) -> "Sequences":
        if self.df is not None:
            xar = self.df_to_xarray(self.df).to_netcdf(path)
        else:
            abspath = os.path.abspath(path)
            os.makedirs(abspath)
            for i, seq in enumerate(self):
                filepath = os.path.join(abspath, str(i))
                seq.to_xarray().to_netcdf(filepath)
        return self

    @staticmethod
    def _create_hdf5_datasets(h5f: h5.File,
                              proto_seq: Sequence,
                              fillvalue: float,
                              resize_length: int,
                              create_dataset_kwargs: dict):
        idxs = np.array(["*".join(map(str, i)) for i in proto_seq.index], dtype=bytes)
        cols = np.array(proto_seq.columns, dtype=bytes)
        index = h5f.create_dataset("index",
                                   (proto_seq.shape[0],),
                                   dtype=idxs.dtype)
        index[:] = idxs
        columns = h5f.create_dataset("columns",
                                     (proto_seq.shape[1],),
                                     dtype=cols.dtype)
        columns[:] = cols
        ###
        if "dtype" in create_dataset_kwargs:
            dtype = create_dataset_kwargs.pop("dtype")
        else:
            dtype = proto_seq.to_numpy().dtype
        maxshape = (None, *proto_seq.shape)
        if "chunks" in create_dataset_kwargs:
            chunks = create_dataset_kwargs.pop("chunks")
        else:
            num_seqs_in_chunk = int((1024 * 1024 * 16) #16MB
                                    / dtype.itemsize
                                    / (proto_seq.shape[0] * proto_seq.shape[1]))
            chunks = (num_seqs_in_chunk, *proto_seq.shape)
        values = h5f.create_dataset("values",
                                    (resize_length, *proto_seq.shape),
                                    maxshape=maxshape,
                                    fillvalue=fillvalue,
                                    dtype=dtype,
                                    chunks=chunks,
                                    **create_dataset_kwargs)
        return values

    def to_hdf5(self,
                path: str,
                resize_length: Optional[int]=None,
                **create_dataset_kwargs) -> "Sequences":
        fillvalue = np.nan
        try:
            resize_length = resize_length or len(self)
        except:
            resize_length = 1

        if self.df is not None:
            LOGGER.debug("Sequences.to_hdf5() from df...")
            seq = self[0]
            with h5.File(path, "w") as h5f:
                values = Sequences._create_hdf5_datasets(h5f, seq, fillvalue, len(self), create_dataset_kwargs)
                data = np.array(self.df.to_numpy().reshape(values.shape), order="C")
                values.write_direct(data)
        # elif self.vci is not None:
        #     raise NotImplementedError
        else:
            LOGGER.debug("Sequences.to_hdf5() from iterable (resize_length=%s)...", resize_length)
            with h5.File(path, "w") as h5f:
                for i, seq in enumerate(self):
                    if (i + 1) % 1000 == 0:
                        LOGGER.debug("Sequences.to_hdf5() written %s tracks, chunks=%s...", i + 1, values.chunks)
                    if i == 0:
                        values = Sequences._create_hdf5_datasets(h5f, seq, fillvalue, resize_length, create_dataset_kwargs)
                    if i > (values.shape[0] - 1):
                        LOGGER.debug("Sequences.to_hdf5() resizing...")
                        values.resize(values.shape[0] + resize_length, 0)
                    values[i] = seq.to_numpy()
                values.resize(i + 1, 0)
        return self

    def to_disk(self, path: str, **kwargs):
        if path.endswith(".nc"):
            self.to_netcdf(path)
        elif path.endswith(".h5"):
            self.to_hdf5(path, **kwargs)
        else:
            raise NotImplementedError

    def to_jsonlines(self) -> Iterable[str]:
        for seq in self:
            yield seq.to_json() + "\n"

    @classmethod
    def _df_iter(cls, df: pd.DataFrame) -> Iterable[Sequence]:
        # Ensure seqidx is level 0:
        df.index.swaplevel(0, cls.IDX_NAMES[0])
        for i in sorted(set(df.index.get_level_values(0))):
            yield Sequence(df.loc[i])

    def _vci_iter(self) -> Iterable[Sequence]:
        for i in range(len(self)):
            yield self[i]

    @classmethod
    def _xr_iter(cls, xar: xr.Dataset) -> Iterable[Sequence]:
        for i in range(xar.dims[cls.IDX_NAMES[0]]):
            df = xar.sel({cls.IDX_NAMES[0]: i}).to_dataframe()
            yield Sequence(Sequences._unpack_multiindex(df))

    @classmethod
    def _unpack_multiindex(cls, df: pd.DataFrame) -> pd.DataFrame:
        if len(df.index.names) == 2:
            df.index = df.reorder_levels([cls.IDX_NAMES[0], "index"]).index
            mi = [(seqidx, int(ilab.split("*")[0]), ilab.split("*")[1])
                  for seqidx, ilab
                  in df.index]
            df.index = pd.MultiIndex.from_tuples(mi, names=cls.IDX_NAMES)
            return df
        elif len(df.index.names) == 1:
            mi = [(int(ilab.split("*")[0]), ilab.split("*")[1])
                  for ilab
                  in df.index]
            df.index = pd.MultiIndex.from_tuples(mi, names=cls.IDX_NAMES[1:])
            return df
        else:
            raise Exception("Wrong index names: {}".format(df.index.names))
