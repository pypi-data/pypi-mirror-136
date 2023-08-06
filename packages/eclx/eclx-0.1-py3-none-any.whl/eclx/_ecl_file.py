"""Load Eclipse 3D property Files
"""
import pathlib
import contextlib
from typing import Type

import numpy as np

from ecl.eclfile import EclFile

from ._grid import load_ecl_grid_index, open_EclGrid
from ._utils import import_tqdm, get_ecl_deck

tqdm = import_tqdm()

_ECL_NON3D_IGNORE = [
    "INTEHEAD",
    "LOGIHEAD",
    "DOUBHEAD",
    "TABDIMS",
    "TAB",
    "TRANNNC",
    "SEQNUM",
    "DLYTIM",
    "STARTSOL",
    "ENDSOL",
    "CON",
    "NNCHEAD",
    "IGRP",
]


@contextlib.contextmanager
def open_EclFile(filepath):
    """Safely open an EclFile instance with a context manager"""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input grid file {filepath}")

    efile = None
    # safety clause for loading eclipse data with ecl
    try:
        efile = EclFile(str(filepath))
        yield efile
    except ValueError as e:
        print(e)
        raise ValueError(f"cannot interpret file type {filepath}")
    finally:
        del efile


def get_ecl_property_keys(filepath):
    """Get the Keywords in an ecl file"""
    with open_EclFile(filepath) as efile:
        keys = efile.keys()
        return [key for key in keys if key not in _ECL_NON3D_IGNORE]


def load_ecl_property(
    filepath,
    report_index=0,
    grid_filepath=None,
    keys=None,
    ignore_keys=None,
    silent=True,
):
    """Load a kw grid property from the simulation output files

    keys are loaded into `pandas.DataFrame` `self.data`.

    Args:
        filepath (pathlike) -- Full file name and path
        keys (list/str, optional): Key or list of keys to load.
            Defaults to None - loads all keys.
        ignore_keys

    Returns:

    """
    deck_files = get_ecl_deck(filepath)

    if grid_filepath is None and not deck_files["GRID"]:
        raise ValueError("Cannot find a grid file for this deck, please specify one.")
    elif grid_filepath is None:
        grid_filepath = deck_files["GRID"][0]  # ecl looks for grid files referenced to the init name

    if keys is None:  # get all keys
        keys_to_load = get_ecl_property_keys(filepath)
    elif isinstance(keys, list):
        keys_to_load = keys
    elif isinstance(keys, str):
        keys_to_load = [keys]
    else:
        raise ValueError("key word argument keys must be None, list or str")

    if ignore_keys:
        keys_to_load = [key for key in keys_to_load if key not in ignore_keys]

    data = load_ecl_grid_index(grid_filepath)
    active_size = data["actnum"].sum()

    try:
        reports = EclFile.file_report_list(str(filepath))
        reports = [f"_{r}" for r in reports]
    except TypeError:
        reports = [""]

    with open_EclFile(filepath) as efile, open_EclGrid(grid_filepath) as egrid:
        # filter to values that are active_size long
        headers = efile.headers
        headers = set(
            map(lambda x: x[0], filter(lambda x: x[1] == active_size, headers))
        )
        ktl = headers.intersection(keys_to_load)

        for var in (pbar := tqdm(ktl, disable=silent, leave=True)):
            pbar.set_description(f"Loading KW: {var}")
            try:
                # non-active cells need to be filled for this work
                kw = efile.iget_named_kw(var, report_index)
                report_n = reports[report_index]
                var_np = egrid.create3D(kw)
                data[f"{var}{report_n}"] = np.moveaxis(
                    var_np, (0, 1, 2), (2, 1, 0)
                ).flatten()
            except KeyError:
                raise ValueError("The keyword {var} is not in the ecl file.")

    return data
