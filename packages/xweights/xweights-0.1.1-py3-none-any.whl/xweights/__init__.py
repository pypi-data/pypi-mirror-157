# -*- coding: utf-8 -*-
# flake8: noqa

"""Top-level package for xweights."""

import warnings

from . import _regions as regions
from ._domains import get_domain, which_domains
from ._io import Input, adjust_name
from ._regions import get_region, which_regions, which_subregions
from ._tabulator import concat_dataframe, write_to_csv
from ._weightings import get_spatial_averager, spatial_averager
from .data import netcdf as test_netcdf
from .data import shp as test_shp
from .xweights import compute_weighted_means, compute_weighted_means_ds

warnings.simplefilter(action="ignore", category=FutureWarning)

__author__ = """Ludwig Lierhammer"""
__email__ = "ludwig.lierhammer@hereon.de"
__version__ = "0.1.1"
