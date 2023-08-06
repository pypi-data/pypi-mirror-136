"""Load Eclipse Summary Files
"""

import pathlib
import contextlib
from typing import Type

from ecl.summary import EclSum

@contextlib.contextmanager
def open_EclSum(filepath):
    """Safely open an EclSum instance with a context manager"""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input summary file {filepath}")

    efile = None
    # safety clause for loading eclipse data with ecl
    try:
        efile = EclSum(str(filepath))
        yield efile
    except ValueError as e:
        print(e)
        raise ValueError(f"cannot interpret file type {filepath}")
    finally:
        del efile


def get_summary_keys(filepath):
    """Load the curves keys from an Eclipse deck"""
    with open_EclSum(filepath) as esum:
        return list(esum.keys())


def load_summary_df(filepath, curves=None):
    """Load a summary from an Eclipse deck as a pandas dataframe.

    Args:
        filepath ([type]): [description]
        curves (list): A list of curve keys to load.


    """
    _has_curves = get_summary_keys(filepath)

    if curves:
        unknown_curves = [
            c for c in curves if c not in _has_curves
        ]
    else:
        curves = _has_curves
        unknown_curves = []

    if unknown_curves:
        raise ValueError(f"Summary does not contain curves: {unknown_curves}")

    with open_EclSum(filepath) as esum:
        sum_df = esum.pandas_frame(column_keys=curves).copy()

    return sum_df
