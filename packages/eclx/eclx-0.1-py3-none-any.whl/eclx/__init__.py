from ._version import version as __version__

from ._ecldeck import EclDeck
from ._utils import get_filetype, get_ecl_deck
from ._ecl_file import (
    open_EclFile,
    load_ecl_property,
    load_ecl_grid_index,
    get_ecl_property_keys,
)
from ._grid import open_EclGrid, load_ecl_grid
from ._init import load_init_intehead
from ._rst import load_ecl_rst, get_restart_reports
from ._sum import get_summary_keys, load_summary_df, open_EclSum
