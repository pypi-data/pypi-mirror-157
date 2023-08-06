
import pytest

import xweights as xw

from . import has_intake, requires_intake
from . import has_dask, requires_dask

def test_get_dataset_dict():
    netcdffile = xw.test_netcdf[0]
    assert xw.Input(netcdffile).dataset_dict
