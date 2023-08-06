"""Load Eclipse Grid Files
"""
import pathlib
import contextlib

import pandas as pd

from ecl import EclFileEnum
from ecl.eclfile import EclFile

from ._ecl_file import open_EclFile, load_ecl_property
from ._utils import import_tqdm, get_ecl_deck

tqdm = import_tqdm()


def is_restart_file(filepath):
    """Check if a given file is an Eclipse restart file"""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input restart file {filepath}")

    file_type, report_step, fmt_file = EclFile.getFileType(str(filepath))

    return file_type in [
        EclFileEnum.ECL_RESTART_FILE,
        EclFileEnum.ECL_UNIFIED_RESTART_FILE,
    ]


def is_restart_unified(filepath):
    """Check if a restart file is unified or split by reports"""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input restart file {filepath}")

    file_type, report_step, fmt_file = EclFile.getFileType(str(filepath))
    return file_type == EclFileEnum.ECL_UNIFIED_RESTART_FILE


def _get_restart_reports_unified(filepath):
    """Get the restart report df if the restart file is unified"""
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot find input restart file {filepath}")

    reports = EclFile.file_report_list(str(filepath))

    with open_EclFile(filepath) as erst:
        edates = erst.dates

    dates = [d.strftime("%Y-%m-%d") for d in edates]
    year = [d.year for d in edates]
    month = [d.month for d in edates]
    day = [d.day for d in edates]
    ordinal = [d.toordinal() for d in edates]

    report_df = pd.DataFrame(
        data=dict(
            report=reports, date=dates, year=year, month=month, day=day, ordinal=ordinal
        )
    )
    report_df["file"] = str(filepath)
    report_df["file_index"] = report_df.index.values
    return report_df


def _get_restart_reports_ununified(filepaths):
    """Get the restart report df if the restart is split into files"""
    reports = [
        _get_restart_reports_unified(filepath) for filepath in filepaths
    ]
    report_df = pd.concat(reports).reset_index(drop=True)
    return report_df

def get_restart_reports(filepath):
    """Get the list of restart files."""
    assert is_restart_file(filepath)

    if is_restart_unified(filepath):
        return _get_restart_reports_unified(filepath)
    else:
        deck_files = get_ecl_deck(filepath)
        return _get_restart_reports_ununified(deck_files["RST"])


def load_ecl_rst(filepath, grid_filepath=None, reports=None, keys=None, silent=True):
    """ """
    dates = get_restart_reports(filepath)

    # only load requested reports
    if reports is None:
        reports = dates["report"].to_list()
    elif isinstance(reports, int):
        reports = [reports]
    elif not isinstance(reports, list):
        raise ValueError("Report should be one of None, int or list[int]")

    dates = dates[dates["report"].isin(reports)]

    # test requested reports are available
    try:
        assert set(reports) == set(dates.report)
    except AssertionError:
        missing = set(reports).difference(dates.report)
        raise ValueError(f"Report values are not in restart file: {missing}")

    data = None
    with tqdm(total=dates.shape[0], disable=silent) as pbar:
        for i, vals in dates.iterrows():
            pbar.set_description(f"Loading RST Report {vals['report']}")
            _td = load_ecl_property(
                vals["file"],
                keys=keys,
                grid_filepath=grid_filepath,
                report_index=vals["file_index"],
                silent=silent,
            )

            if data is not None:
                data = data.join(_td.iloc[:, 5:])
            else:
                data = _td
            pbar.update()

    return data
