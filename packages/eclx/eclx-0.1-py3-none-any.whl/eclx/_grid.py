"""Load Eclipse Grid Files
"""
import pathlib
import itertools
import contextlib

import pandas as pd

from ecl.grid import EclGrid

from ._utils import import_tqdm, get_filetype, EclFileEnum

tqdm = import_tqdm()

GRID_FILE_TYPES = [EclFileEnum.ECL_GRID_FILE, EclFileEnum.ECL_EGRID_FILE]


def _corner_names():
    """create corner names list so they can be easily referenced later"""
    return [
        f"{dim}{n}"
        for (n, dim) in itertools.product(
            range(8),
            ("x", "y", "z"),
        )
    ]


def _xcorn_names():
    return [c for c in _corner_names() if "x" in c]


def _ycorn_names():
    return [c for c in _corner_names() if "y" in c]


def _zcorn_names():
    return [c for c in _corner_names() if "z" in c]


@contextlib.contextmanager
def open_EclGrid(filepath):
    """Safely open an EclGrid instance with a context manager"""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input grid file {filepath}")

    egrid = None
    # safety clause for loading eclipse data with ecl
    try:
        file_type = get_filetype(filepath)
        if file_type not in GRID_FILE_TYPES:
            raise ValueError
        egrid = EclGrid.load_from_file(str(filepath.absolute()))
        yield egrid
    except (ValueError, OSError): # OSError on windows
        raise ValueError(f"cannot interpret file type {filepath}")
    finally:
        del egrid


def get_ecl_grid_dims(filepath):
    """Get the dimensions of the grid

    Args:

    Returns:
        tuple: i, j, k dim sizes
    """
    with open_EclGrid(filepath) as egrid:
        return (
            egrid.nx,
            egrid.ny,
            egrid.nz,
        )


def load_ecl_grid_index(filepath, silent=True):
    """Load a simulation grid index

    Args:

    Returns:

    """
    with open_EclGrid(filepath) as egrid:
        data = egrid.export_index()
        data["actnum"] = egrid.export_actnum().numpy_copy()

    return data


def load_ecl_grid(filepath, silent=True):
    """Load a simulation grid

    Args:

    Returns:

    """
    with open_EclGrid(filepath) as egrid:
        xyzcorn = pd.DataFrame(egrid.export_index())
        zcorn = egrid.export_corners(egrid.export_index())

        # create zcorn names list so they can be easily referenced later
        cnames = _corner_names()
        for c, zc in enumerate(cnames):
            xyzcorn[zc] = zcorn[:, c]

    return xyzcorn
