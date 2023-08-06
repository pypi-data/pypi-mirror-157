
import pytest

import xweights as xw
import xarray as xr

from . import has_dask, requires_dask
from . import has_geopandas, requires_geopandas
from . import has_intake, requires_intake
from . import has_numpy, requires_numpy
from . import has_xarray, requires_xarray
from . import has_cordex, requires_cordex
from . import has_xesmf, requires_xesmf

def test_compute_weighted_means_ds():
    netcdffile = xw.test_netcdf[0]
    shp = xw.get_region('states')
    ds = xr.open_dataset(netcdffile)
    df = xw.compute_weighted_means_ds(ds, shp, 
                                      time_range=['2007-01-01','2007-11-30'],
                                      column_names=['institute_id',
                                                    'driving_model_id',
                                                    'experiment_id',
                                                    'driving_model_ensemlbe_member',
                                                    'model_id',
                                                    'rcm_version_id'])

def test_compute_weighted_means():
    netcdffile = xw.test_netcdf[0]
    df = xw.compute_weighted_means(netcdffile,
                                   region='states',
                                   subregion=['01_Schleswig-Holstein',
                                              '02_Hamburg',
                                              '03_Niedersachsen',
                                              '04_Bremen'],
                                   merge_columns=['all','NorthSeaCoast'],)
