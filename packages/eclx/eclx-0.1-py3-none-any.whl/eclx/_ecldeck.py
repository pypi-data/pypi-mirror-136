"""Interface for users to ecl by Statoil/Equinor

This interface builds entirely upon the ecl project.
https://github.com/Equinor/ecl

ecl is a library designed to interface directly with
Eclipse simulation files.

"""
# pylint: disable=invalid-name

import pathlib

import numpy as np
import pandas as pd

# from ecl import EclFileEnum
# from ecl.grid.ecl_grid import EclGrid
# from ecl.eclfile import EclFile
# from ecl.eclfile.ecl_restart_file import EclRestartHead

# from etlpy.core.exceptions import WorkflowError

from ._ecl_file import load_ecl_property
from ._grid import (
    load_ecl_grid_index,
    load_ecl_grid,
    get_ecl_grid_dims,
    _xcorn_names,
    _ycorn_names,
    _zcorn_names,
)
from ._init import load_init_intehead
from ._rst import is_restart_file, get_restart_reports, load_ecl_rst
from ._utils import import_tqdm

tqdm = import_tqdm()


class EclDeck:
    """A class to encapsulate Eclipse Simulator Output Methods and Properties"""

    def __init__(self, silent=False):
        """Constructor

        Args:
            silent (bool, optional): Defaults to False, disable progress bars,
                log output
        """
        self.data = pd.DataFrame()
        self.egrid_file = None
        self.einit_file = None
        self.erst_file = None
        self.silent = silent
        self.loaded_reports = None
        self.nx = None
        self.ny = None
        self.nz = None
        self.mapaxes = None
        self.active = None
        self.coord = None
        self.xyzcorn = None
        self.zcorn_names = None
        self._xcorn_names = None
        self._ycorn_names = None
        self._zcorn_names = None
        self.keys_init = None
        self.init_intehead = dict()
        self.reports = None
        self.reports_dict = dict()
        self.dates = None

    def set_grid(self, filepath):
        """Set the simulation grid file and initialise ecl link

        Arguments:
            filename {string}: Full file name and path
        """
        filepath = pathlib.Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Cannot find input file {filepath}")
        self.egrid_file = filepath

    def load_grid(self, filename=None):
        """Load the simulation grid file

        Arguments:
            filename (string): Defaults to None; Full file name and path
        """
        if filename is not None:
            self.set_grid(filename)
        elif self.egrid_file is None:
            raise ValueError("grid file has not been specified")

        self.nx, self.ny, self.nz = get_ecl_grid_dims(self.egrid_file)
        self.data = load_ecl_grid_index(self.egrid_file, silent=self.silent)
        self.xyzcorn = load_ecl_grid(self.egrid_file, silent=self.silent)

        self.data["centerx"] = self.xyzcorn[_xcorn_names()].mean(axis=1)
        self.data["centery"] = self.xyzcorn[_ycorn_names()].mean(axis=1)
        self.data["centerz"] = self.xyzcorn[_zcorn_names()].mean(axis=1)

    @property
    def corner_names(self):
        """The names of corner coordinates in self.xyzcorn"""
        return _xcorn_names() + _ycorn_names() + _zcorn_names()

    def set_init(self, filepath):
        """Set the init simulation file

        Args:
            filepath (string): Full file name and path
        """
        filepath = pathlib.Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Cannot find input file {filepath}.")
        self.einit_file = filepath

    def load_init(self, filepath=None, keys=None):
        """Load the init simulation file

        keys are loaded into `pandas.DataFrame` `self.data`.

        Args:
            filepath (string) -- Full file name and path
            keys (list/str, optional): Key or list of keys to load.
                Defaults to None - loads all keys.
        """

        if filepath is not None:
            self.set_init(filepath)
        elif self.einit_file is None:
            raise ValueError("init file has not been specified")

        self.init_intehead = load_init_intehead(self.einit_file)

        # sanity checks
        if (
            self.init_intehead["NI"] != self.nx
            or self.init_intehead["NJ"] != self.ny
            or self.init_intehead["NK"] != self.nz
        ):
            raise ValueError("INIT file grid dimensions do not match grid dimensions.")

        data = load_ecl_property(
            self.einit_file,
            grid_filepath=self.egrid_file,
            keys=keys,
            silent=self.silent,
            report_index=0,
        )

        if self.data.empty:
            self.data = data
        else:
            self.data = self.data.join(data.iloc[:, 5:])

    def set_rst(self, filepath):
        """Load the report list and create report list dictionary

        Arguments:
            filepath (pathlike) -- The full path to the restart file.

        """
        filepath = pathlib.Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Cannot find input file {filepath}.")
        self.erst_file = str(filepath)

        if not is_restart_file(filepath):
            raise ValueError(
                f"The input filename {filepath} does not correspond to a restart file.  Please follow the Eclipse naming conventions"
            )

        self.dates = get_restart_reports(filepath)
        self.reports = self.dates["report"].to_list()

    def load_rst(self, reports=None, keys=None):
        """Load the restart file

        Arguments:
            reports ('all'/list) -- A list of report numbers else
                                     loads 'all' reports
        """
        if reports is None:
            reports = self.dates["report"].to_list()
        elif isinstance(reports, int):
            reports = [reports]
        elif not isinstance(reports, list):
            raise ValueError("Report should be one of None, int or list[int]")

        data_rst = load_ecl_rst(
            self.erst_file,
            grid_filepath=self.egrid_file,
            reports=reports,
            keys=keys,
            silent=self.silent,
        )

        if self.data.empty:
            self.data = data_rst
        else:
            self.data = self.data.join(data_rst.iloc[:, 5:])

        self.loaded_reports = reports

        # # error reporting
        # if len(failed_keys) > 0:
        #     msg = "Invalid 3D KWs:" + ", ".join(failed_keys)
        #     print(msg)
        # if len(missing_keys) > 0:
        #     msg = "Missing requested 3D KWs:" + ", ".join(missing_keys)
        #     print(msg)

    def get_celldz_mean(self, df):
        """Calculates the minimum height of all active cells.

        This method is simple and relies on the diference between vertical corners
        that may also have an X, Y offset.
        """
        dz = np.zeros_like(df.x1)
        for i in range(0, 4):
            a = self._zcorn_names[i]
            b = self._zcorn_names[i + 4]
            dz += df[b] - df[a].values
            return dz / 4
