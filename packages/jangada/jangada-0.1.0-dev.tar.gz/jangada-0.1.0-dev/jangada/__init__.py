#  -*- coding: utf-8 -*-
"""

Author: Rafael R. L. Benevides
Date: 10/03/2021

"""


import pandas

pandas.plotting.register_matplotlib_converters()


# ========== ========== ========== ========== ========== ==========
from .settings import Settings


# ========== ========== ========== ========== ========== ==========
settings = Settings()


# ========== ========== ========== ========== ========== ==========
# from jangada.timeseries import TimeSeries, TimeSeriesFrame, TimeSeriesDatabase


__version__ = '0.1.0-dev'
__author__ = 'The Jangada Development Team'
