"""Load Eclipse INIT Files
"""
import numpy as np
import pandas as pd

from ._ecl_file import open_EclFile
from ._eclmaps import InitIntheadMap
from ._utils import import_tqdm

tqdm = import_tqdm()


def load_init_intehead(filepath):
    """From init load integer header array for important variables

    Args:
        filepath

    Returns:
        (dict)

    Notes:
        The following items are significant:
            Item 3 - units type: 1 - METRIC, 2 - FIELD, 3 - LAB,
                                 4 - PVT-M
            Items 9, 10, 11 - grid dimensions NX, NY and NZ
            Item 12 - NACTIV = number of active cells
            Item 14 - grid type. 0 - Corner point, 1 - Unstructured,
                                 2 - Hybrid, 3 - Block center
            Item 15 - IPHS = phase indicator:1 - oil,
                                             2 - water,
                                             3 - oil/water,
                                             4 - gas,
                                             5 - oil/gas,
                                             6 - gas/water,
                                             7 - oil/water/gas (ECLIPSE output only)

            Item 65 - IDAY = calendar day at start of run (1-31)
            Item 66 - IMON = calendar month at start of run (1-12)
            Item 67 - IYEAR = calendar year at start of run (as four
                              digits, for example 1952)
            Item 95 - IPROG = simulation program identifier:
                100 - ECLIPSE 100
                300 - ECLIPSE 300
                500 - ECLIPSE 300 (thermal option)
                700 - INTERSECT
                800 - FrontSim
                negative - Other simulator
            Item 207- IHOURZ = current simulation time
                HH:MM:SS - number of hours (HH) (0-23).
            Item 208- IMINTS = current simulation time
                HH:MM:SS - number of minutes (MM) (0-59).
            Item 411- ISECND = current simulation time
                HH:MM:SS - number of seconds (SS), reported in
                microseconds (0-59,999,999).
            Undefined items in this array may be set to zero.


    """

    with open_EclFile(filepath) as einit:
        intehead = einit.iget_named_kw("INTEHEAD", 0)
        intehead = intehead.numpy_view()

    init_intehead = dict()

    for enum in InitIntheadMap:
        init_intehead[enum.name] = intehead[enum.value]

    return init_intehead
