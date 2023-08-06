# -*- mode: python; coding: utf-8 -*-
# vim: set ft=python:
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

"""Convenience utilities."""

import inspect
from collections import namedtuple
from contextlib import contextmanager
from typing import Iterable, Union
from functools import partial
from operator import contains
import numpy as np
from . import (
    ContactSolver,
    Model,
    SurfaceGenerator1D,
    SurfaceGenerator2D,
    dtype,
    set_log_level,
    get_log_level,
    LogLevel,
    Logger,
)

__all__ = [
    "log_context",
    "publications",
    "load_path",
    "seeded_surfaces",
    "hertz_surface",
]


class NoConvergenceError(RuntimeError):
    """Convergence not reached exception."""


@contextmanager
def log_context(log_level: LogLevel):
    """Context manager to easily control Tamaas' logging level."""
    current = get_log_level()
    set_log_level(log_level)
    try:
        yield
    finally:
        set_log_level(current)


def publications(format_str="{pub.citation}\n\t{pub.doi}"):
    """Print publications associated with objects in use."""
    Publication = namedtuple("Publication", ["citation", "doi"])
    joss = Publication(
        citation=(
            "Frérot, L., Anciaux, G., Rey, V., Pham-Ba, S. & Molinari, J.-F."
            " Tamaas: a library for elastic-plastic contact of periodic rough"
            " surfaces. Journal of Open Source Software 5, 2121 (2020)."),
        doi="10.21105/joss.02121",
    )

    zenodo = Publication(
        citation=(
            "Frérot, Lucas, Anciaux, Guillaume, Rey, Valentine, Pham-Ba, Son, "
            "& Molinari, Jean-François. (2022). Tamaas, a high-performance "
            "library for periodic rough surface contact (2.4.0). Zenodo."),
        doi="10.5281/zenodo.3479236",
    )

    _publications = {
        k: v
        for keys, v in [
            (
                (
                    "SurfaceGeneratorRandomPhase1D",
                    "SurfaceGeneratorRandomPhase2D",
                ),
                [
                    Publication(
                        citation=(
                            "Wu, J.-J. Simulation of rough surfaces with FFT."
                            " Tribology International 33, 47–58 (2000)."),
                        doi="10.1016/S0301-679X(00)00016-5",
                    ),
                ],
            ),
            (
                ("SurfaceGeneratorFilter1D", "SurfaceGeneratorFilter2D"),
                [
                    Publication(
                        citation=(
                            "Hu, Y. Z. & Tonder, K. Simulation of 3-D random"
                            " rough surface by 2-D digital filter and fourier"
                            " analysis. International Journal of Machine Tools"
                            " and Manufacture 32, 83–90 (1992)."),
                        doi="10.1016/0890-6955(92)90064-N",
                    ),
                ],
            ),
            (
                ("PolonskyKeerRey", ),
                [
                    Publication(
                        citation=(
                            "Polonsky, I. A. & Keer, L. M. A numerical method"
                            " for solving rough contact problems based on the"
                            " multi-level multi-summation and conjugate"
                            " gradient techniques. Wear 231, 206–219 (1999)."),
                        doi="10.1016/S0043-1648(99)00113-1",
                    ),
                    Publication(
                        citation=(
                            "Rey, V., Anciaux, G. & Molinari, J.-F. Normal"
                            " adhesive contact on rough surfaces: efficient"
                            " algorithm for FFT-based BEM resolution. Comput"
                            " Mech 1–13 (2017)."),
                        doi="10.1007/s00466-017-1392-5",
                    ),
                ],
            ),
            (
                ("DFSANESolver", "DFSANECXXSolver"),
                [
                    Publication(
                        citation=(
                            "La Cruz, W., Martínez, J. & Raydan, M. Spectral"
                            " residual method without gradient information for"
                            " solving large-scale nonlinear systems of"
                            " equations. Math. Comp. 75, 1429–1448 (2006)."),
                        doi="10.1090/S0025-5718-06-01840-0",
                    ),
                ],
            ),
            (
                ("Residual", ),
                [
                    Publication(
                        citation=("Frérot, L., Bonnet, M., Molinari, J.-F. &"
                                  " Anciaux, G. A Fourier-accelerated volume"
                                  " integral method for elastoplastic contact."
                                  " Computer Methods in Applied Mechanics and"
                                  " Engineering 351, 951–976 (2019)."),
                        doi="10.1016/j.cma.2019.04.006",
                    ),
                ],
            ),
            (
                ("EPICSolver", ),
                [
                    Publication(
                        citation=("Frérot, L., Bonnet, M., Molinari, J.-F. &"
                                  " Anciaux, G. A Fourier-accelerated volume"
                                  " integral method for elastoplastic contact."
                                  " Computer Methods in Applied Mechanics and"
                                  " Engineering 351, 951–976 (2019)."),
                        doi="10.1016/j.cma.2019.04.006",
                    ),
                    Publication(
                        citation=(
                            "Jacq, C., Nélias, D., Lormand, G. & Girodin, D."
                            " Development of a Three-Dimensional"
                            " Semi-Analytical Elastic-Plastic Contact Code."
                            " Journal of Tribology 124, 653 (2002)."),
                        doi="10.1115/1.1467920",
                    ),
                ],
            ),
            (
                ("Condat", ),
                [
                    Publication(
                        citation=(
                            "Condat, L. A Primal–Dual Splitting Method for"
                            " Convex Optimization Involving Lipschitzian,"
                            " Proximable and Linear Composite Terms. J Optim"
                            " Theory Appl 158, 460–479 (2012)."),
                        doi="10.1007/s10957-012-0245-9",
                    ),
                ],
            ),
            (
                ("KatoSaturated", ),
                [
                    Publication(
                        citation=(
                            "Stanley, H. M. & Kato, T. An FFT-Based Method for"
                            " Rough Surface Contact. J. Tribol 119, 481–485"
                            " (1997)."),
                        doi="10.1115/1.2833523",
                    ),
                    Publication(
                        citation=(
                            "Almqvist, A., Sahlin, F., Larsson, R. &"
                            " Glavatskih, S. On the dry elasto-plastic contact"
                            " of nominally flat surfaces. Tribology"
                            " International 40, 574–579 (2007)."),
                        doi="10.1016/j.triboint.2005.11.008",
                    ),
                ],
            ),
        ] for k in keys
    }

    frame = inspect.stack()[1][0]
    caller_vars = (frame.f_globals | frame.f_locals)
    citable = filter(
        partial(contains, _publications.keys()),
        map(lambda x: type(x).__name__, caller_vars.values()),
    )

    citable = [joss, zenodo] \
        + list({pub for k in citable for pub in _publications[k]})

    msg = "Please cite the following publications:\n\n"
    msg += "\n".join(format_str.format(pub=pub) for pub in citable)

    Logger().get(LogLevel.info) << msg

    return citable


def load_path(
    solver: ContactSolver,
    loads: Iterable[Union[float, np.ndarray]],
    verbose: bool = False,
    callback=None,
) -> Iterable[Model]:
    """
    Generate model objects solutions for a sequence of applied loads.

    :param solver: a contact solver object
    :param loads: an iterable sequence of loads
    :param verbose: print info output of solver
    :param callback: a callback executed after the yield
    """
    log_level = LogLevel.info if verbose else LogLevel.warning

    with log_context(log_level):
        for load in loads:
            if solver.solve(load) > solver.tolerance:
                raise NoConvergenceError("Solver error exceeded tolerance")

            yield solver.model

            if callback is not None:
                callback()


def seeded_surfaces(
    generator: Union[SurfaceGenerator1D, SurfaceGenerator2D],
    seeds: Iterable[int],
) -> Iterable[np.ndarray]:
    """
    Generate rough surfaces with a prescribed seed sequence.

    :param generator: surface generator object
    :param seeds: random seed sequence
    """
    for seed in seeds:
        generator.random_seed = seed
        yield generator.buildSurface()


def hertz_surface(system_size: Iterable[float], shape: Iterable[int],
                  radius: float) -> np.ndarray:
    """
    Construct a parabolic surface.

    :param system_size: size of the domain in each direction
    :param shape: number of points in each direction
    :param radius: radius of surface
    """
    coords = map(
        lambda L, N: np.linspace(0, L, N, endpoint=False, dtype=dtype),
        system_size,
        shape,
    )
    coords = np.meshgrid(*coords, "ij", sparse=True)
    surface = (-1 / (2 * radius)) * sum(
        (x - L / 2)**2 for x, L in zip(coords, system_size))
    return surface


def radial_average(x, y, values, r, theta, method='linear', endpoint=False):
    """Compute the radial average of a 2D field."""
    try:
        from scipy.interpolate import RegularGridInterpolator
    except ImportError:
        raise ImportError("Install scipy to use tamaas.utils.radial_average")

    interpolator = RegularGridInterpolator((x, y), values, method=method)
    rr, tt = np.meshgrid(r, theta, indexing='ij', sparse=True)
    x, y = rr * np.cos(tt), rr * np.sin(tt)
    X = np.vstack((x.flatten(), y.flatten())).T
    return interpolator(X).reshape(x.shape).sum(axis=1) \
        / (theta.size - int(not endpoint))
