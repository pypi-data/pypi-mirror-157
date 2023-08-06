from ._domains import get_domain

import warnings

def adjust_vertices(ds, domain_name=None):
    """Set correct lon and lat vertices to xr.Dataset

    Parameters
    ----------
    ds: xr.Dataset

    domain_name: str (optional)
        If `ds` does not contain lon and lat vertices take them from CORDEX domain dataset

    Returns
    -------
    xr.Dataset
        Dataset containing correct lon and lat vertices

    """

    def roll_vertices(bounds):
        return bounds.roll(vertices=-1)

    def correct_bounds(ds, bounds_name):
        bounds = ds.cf.get_bounds(bounds_name)
        return roll_vertices(bounds)

    def adjust_lat_lon_vertices(ds, coord_name=None, domain_name=None):

        if not ds: return
        coord = ds.cf.coordinates[coord_name]

        try:
            dimlen = len(ds[coord].dims)
        except:
            dimlen = len(ds[coord[0]].dims)
        if dimlen > 1:
            if hasattr(ds.coords[coord[0]], 'bounds'):
                pass
                #bounds = correct_bounds(ds, 'coord_name')
                #ds_[bounds.name] = bounds
            elif hasattr(ds.coords[coord[0]], 'vertices'):
                pass
            else:
                warnings.warn('No {} bounds found in file. Get bounds from example domain dataset.'.format(coord_name))
                if not domain_name:
                    warnings.warn('No example domain is specified')
                    return
                domain = get_domain(domain_name)
                bounds = correct_bounds(domain, coord_name)
                try:
                    ndims_o=len(ds.dims)
                    ds[bounds.name] = bounds
                    ds[bounds.name].values = bounds.values
                    ds[coord[0]].attrs['bounds'] = bounds.name
                    ndims_n=len(ds.dims)
                    if ndims_o != ndims_n: error_exit
                except:
                    warnings.warn('Input grid file does not match example domain dataset grid.')
                    return
        return ds

    ds_c = ds.copy()
    ds_c = adjust_lat_lon_vertices(ds_c, coord_name='longitude', domain_name=domain_name)
    ds_c = adjust_lat_lon_vertices(ds_c, coord_name='latitude', domain_name=domain_name)

    return ds_c
