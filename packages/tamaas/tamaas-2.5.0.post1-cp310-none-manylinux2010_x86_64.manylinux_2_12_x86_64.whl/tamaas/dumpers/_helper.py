# -*- mode:python; coding: utf-8 -*-
#
# Copyright (©) 2016-2022 EPFL (École Polytechnique Fédérale de Lausanne),
# Laboratory (LSMS - Laboratoire de Simulation en Mécanique des Solides)
# Copyright (©) 2020-2022 Lucas Frérot
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Helper functions for dumpers
"""
from os import PathLike
from functools import wraps
from pathlib import Path

import io
import numpy as np

from .. import model_type, type_traits, mpi

__all__ = ["step_dump", "directory_dump"]

_basic_types = [t for t, trait in type_traits.items() if trait.components == 1]


def _is_surface_field(field, model):
    def _to_global(shape):
        if len(shape) == len(model.boundary_shape) + 1:
            return mpi.global_shape(model.boundary_shape) + [shape[-1]]
        else:
            return mpi.global_shape(shape)

    b_shapes = [list(model[name].shape) for name in model.boundary_fields]
    shape = list(field.shape)
    return any(shape == s for s in b_shapes) \
        or any(shape == _to_global(s) for s in b_shapes)


def local_slice(field, model):
    n = model.shape
    bn = model.boundary_shape

    gshape = mpi.global_shape(bn)
    offsets = np.zeros_like(gshape)
    offsets[0] = mpi.local_offset(gshape)

    if not _is_surface_field(field, model) and len(n) > len(bn):
        gshape = [n[0]] + gshape
        offsets = np.concatenate(([0], offsets))

    shape = bn if _is_surface_field(field, model) else n
    if len(field.shape) > len(shape):
        shape += field.shape[len(shape):]

    def sgen(offset, size):
        return slice(offset, offset + size, None)

    def sgen_basic(offset, size):
        return slice(offset, offset + size)

    slice_gen = sgen_basic if model_type in _basic_types else sgen
    return tuple(map(slice_gen, offsets, shape))


def step_dump(cls):
    """
    Decorator for dumper with counter for steps
    """
    orig_init = cls.__init__
    orig_dump = cls.dump

    @wraps(cls.__init__)
    def __init__(obj, *args, **kwargs):
        orig_init(obj, *args, **kwargs)
        obj.count = 0

    def postfix(obj):
        return "_{:04d}".format(obj.count)

    @wraps(cls.dump)
    def dump(obj, *args, **kwargs):
        orig_dump(obj, *args, **kwargs)
        obj.count += 1

    cls.__init__ = __init__
    cls.dump = dump
    cls.postfix = property(postfix)

    return cls


def directory_dump(directory=""):
    "Decorator for dumper in a directory"
    directory = Path(directory)

    def actual_decorator(cls):
        orig_dump = cls.dump
        orig_filepath = cls.file_path.fget
        orig_init = cls.__init__

        @wraps(cls.__init__)
        def init(obj, *args, **kwargs):
            orig_init(obj, *args, **kwargs)
            obj.mkdir = kwargs.get('mkdir', True)

        @wraps(cls.dump)
        def dump(obj, *args, **kwargs):
            if mpi.rank() == 0 and getattr(obj, 'mkdir'):
                directory.mkdir(parents=True, exist_ok=True)

            orig_dump(obj, *args, **kwargs)

        @wraps(cls.file_path.fget)
        def file_path(obj):
            if getattr(obj, 'mkdir'):
                return str(directory / orig_filepath(obj))
            return orig_filepath(obj)

        cls.__init__ = init
        cls.dump = dump
        cls.file_path = property(file_path)

        return cls

    return actual_decorator


def hdf5toVTK(inpath, outname):
    """Convert HDF5 dump of a model to VTK."""
    from . import UVWDumper, H5Dumper  # noqa
    UVWDumper(outname, all_fields=True) << H5Dumper.read(inpath)


def netCDFtoParaview(inpath, outname):
    """Convert NetCDF dump of model sequence to Paraview."""
    from . import UVWGroupDumper, NetCDFDumper  # noqa
    dumper = UVWGroupDumper(outname, all_fields=True)
    for model in NetCDFDumper.read_sequence(inpath):
        dumper << model


def file_handler(mode):
    """Decorate a function to accept path-like or file handles."""
    def _handler(func):
        @wraps(func)
        def _wrapped(self, fd, *args, **kwargs):
            if isinstance(fd, (str, PathLike)):
                with open(fd, mode) as fd:
                    return _wrapped(self, fd, *args, **kwargs)
            elif isinstance(fd, io.TextIOBase):
                return func(self, fd, *args, **kwargs)

            raise TypeError(
                f"Expected a path-like or file handle, got {type(fd)}")

        return _wrapped
    return _handler
