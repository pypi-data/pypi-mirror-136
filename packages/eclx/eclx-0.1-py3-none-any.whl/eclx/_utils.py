import importlib
import pathlib
import re
from more_itertools import chunked

from ecl.eclfile import EclFile
from ecl.ecl_util import EclFileEnum, EclUtil


def import_tqdm():
    jup = importlib.util.find_spec("jupyter")
    ipw = importlib.util.find_spec("ipywidgets")

    if jup is not None and ipw is not None:
        from tqdm.auto import tqdm

        return tqdm
    else:
        from tqdm import tqdm

        return tqdm


def _check_ijk_dim(df):
    """Check if a df has the columns i,j&k and return their max values"""
    if set(("i", "j", "k")).issubset(df.columns):
        return df["i"].max(), df["j"].max(), df["k"].max()
    else:
        return (None, None, None)


def get_filetype(filepath):
    """Safely check what type of ecl file it is."""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input grid file {filepath}")

    return EclUtil.get_file_type(str(filepath))


def get_ecl_deck_files(filepath):
    """Scan a folder based upon a DATA file to find all corresponding files."""
    filepath = pathlib.Path(filepath)

    parent_path = filepath.parent
    if not parent_path.exists():
        raise FileNotFoundError(f"Cannot find input deck folder {parent_path}")

    stem = filepath.stem

    deck = {
        deck_file: get_filetype(deck_file)
        for deck_file in parent_path.iterdir()
        if deck_file.stem == stem
    }
    return deck


def get_ecl_deck(filepath):
    """"""
    files = get_ecl_deck_files(filepath)
    found_files = {
        "DATA": (f for f, v in files.items() if v == EclFileEnum.ECL_DATA_FILE),
        "GRID": (
            f
            for f, v in files.items()
            if v in [EclFileEnum.ECL_EGRID_FILE, EclFileEnum.ECL_GRID_FILE]
        ),
        "INIT": (f for f, v in files.items() if v == EclFileEnum.ECL_INIT_FILE),
        "SUM": (
            f
            for f, v in files.items()
            if v in [EclFileEnum.ECL_SUMMARY_FILE, EclFileEnum.ECL_UNIFIED_SUMMARY_FILE]
        ),
        "RST": (
            f
            for f, v in files.items()
            if v
            in [
                EclFileEnum.ECL_RESTART_FILE,
                EclFileEnum.ECL_UNIFIED_RESTART_FILE,
            ]
        ),
    }
    return {k: tuple(sorted(v)) for k, v in found_files.items()}


def write_petrel(
    df, filename, props=None, cols=8, summary_header="all", fliphand=False
):
    """Writes out a Petrel compatable property file for loading from an eclx loaded
    property dataframe.

    Import to Petrel as "ECLIPSE style keywords (grid properties) (ASCII)"

    Arguments:
        data (pd.DataFrame):
        filename (string): Full filename and output path to write to.
        props (list): Defaults to None (write out all properties) If
            fliphand is True then 'i', 'j', and 'k' values must be in props.
        cols (int): Number of values per row
        summary_header {Optional:str}: Write a statistical summary to the top of the
            output file using Pandas Describe. Valid options are 'all' for all cells
            'active' for active cells only  and 'none' for no summary header.
        fliphand (Optional:bool): False by default this will reverse the cell order
            in the J direction. E.g. convert left handed to right handed grids.
            Petrel requires right handed grids for natural import.
    """
    if props is None:
        props = df.columns

    if summary_header == "all":
        summary_props = df.columns
    elif summary_header == "active":
        summary_props = list(df.columns) + ["active"]

    data = df[summary_props]
    ijk_dims = _check_ijk_dim(df)

    with open(filename, "w") as outfile:

        # Setup header for file
        outfile.write("-- Python eclx output to ECLIPSE style keywords\n")
        outfile.write("-- I, J, K\n")
        outfile.write("-- {:d}, {:d}, {:d}\n".format(*ijk_dims))
        outfile.write(f"-- Flip Grid Handedness: {fliphand}\n")
        if summary_header == "active":
            outfile.write(f"-- Active Summary of properties in file:\n")
        else:
            outfile.write(f"-- Properties in file:\n")
        if summary_header in ["all", "active"]:
            query = "active > 0"
            for gprp in chunked(props, 5):
                outfile.write("-- ")
                if summary_header == "all":
                    data_des = data[list(gprp)].describe().to_string()
                elif summary_header == "active":
                    data_des = data.query(query)[list(gprp)]
                    data_des = data_des.describe().to_string()
                data_des = data_des.replace("\n", "\n-- ")
                outfile.write(data_des + "\n")
        else:
            for gprp in chunked(props, 5):
                outfile.write("-- ")
                for prp in gprp:
                    outfile.write(prp + " ")
                outfile.write("\n")
        # line format
        # TODO: Perhaps offer fmt options for numbers.
        def line_formatter(n, fmt="3.12g"):
            return "".join([" {%d:%s}" % (d, fmt) for d in range(0, n)])

        fmt = line_formatter(cols)

        if fliphand and "j" in data.columns:
            data["j"] = 1 + data["j"].max() - data["j"]
            data = data.sort_values(["k", "j", "i"])
        else:
            data["j"] = data["j"] + 1

        # write data to file
        for prp in props:
            outfile.write(f"{prp}\n")
            try:
                for group in chunked(data[prp], cols):
                    outfile.write(fmt.format(*group) + "\n")
            except IndexError:
                remfmt = line_formatter(len(group))
                outfile.write(remfmt.format(*group) + "\n")
            outfile.write("/\n")
