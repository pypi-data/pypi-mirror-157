import os
import warnings
import xarray as xr
import glob
import intake
import dask
import numpy as np
import cordex as cx

def get_variable_name(ds):
    """List of CF variables in xr.Dataset

    Parameters
    ----------
    ds: xr.Dataset
        xarray Dataset

    Returns
    -------
    list
        List of CF variables
    """
    
    def condition(ds, var):
        return len(ds[var].coords) == len(ds.coords)
    
    def most_coords(ds):
        coords=0
        name=[]
        for var in ds.data_vars:
            ncoords=len(ds[var].coords)
            if ncoords > coords:
                coords=ncoords
                name+=[var]
        return name

    try:
        var_list = [var for var in ds.data_vars if condition(ds, var)]
        if var_list: return var_list
        return most_coords(ds)
    except:
        return [ds.name]

def adjust_name(string):
    """Delete special character from string and replace umlauts.
    If string is a directory path: Replace slashes with underscores
    If string is a netCDF file name: Delete directory path and suffix

    Parameters
    ----------
    string: str

    Returns
    -------
    str

    Example
    -------
    Adjust name of string:

        import xweights as xw

        string =  '/work/kd0956/CORDEX/data/cordex/output/EUR-11/CLMcom/MIROC-MIROC5/rcp85/r1i1p1/CLMcom-CCLM4-8-17/v1/mon/tas/v20171121/tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc'

        new_string = xw.adjust_name(string)

        new_string: tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_200601-201012

    """
    string = string.replace(' ','-')
    string = string.replace('(','')
    string = string.replace(')','')
    string = string.replace('ä','ae')
    string = string.replace('ö','oe')
    string = string.replace('ü','ue')
    string = string.replace('ß','ss')
    if '.nc' in string:
        return string.split('/')[-1].split('.nc')[0]
    elif '/' in string:
        return '_'.join(string.split('/'))[1:]
    else:
        return string

def create_newname(vars, name):
    """Create new name for string

    Parameters
    ----------
    vars: list
        List of CF variables
    name: str
        
    Returns
    -------
    str
    """

    def newname(name, var):
        if var not in name: name = '{}.{}'.format(var, name)
        return name
    return adjust_name([newname(name, var) for var in vars][0])

class Input:
    """The :class:`Input` creates a dataset dictionary containing all given input files
    dataset_dict = {name_of_xrDataset : xrDataset}
    Valid input files are netCDF file(s), directories containing those files and intake-esm catalogue files

    **Attributes:**
        *dataset_dict:*
            dictionary

    Example
    -------
       To create a xarray dataset dictionary from intake-esm catalogue file using some extra filter options::

           import xweights as xw

           catfile = '/work/kd0956/Catalogs/mistral-cordex.json'

           dataset_dict = xw.Input(catfile, variable_id=tas, experiment_id=rcp85, table_id=mon)
       
       To create a xarray dataset dictionary from netCDF file on disk::

           import xweights as xw

           netcdffile = '/work/kd0956/CORDEX/data/cordex/output/EUR-11/CLMcom/MIROC-MIROC5/rcp85/r1i1p1/CLMcom-CCLM4-8-17/v1/mon/tas/v20171121/tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc'

           dataset_dict = xw.Input(netcdffile).dataset_dict

    """

    def  __init__(self, input, **kwargs):
        self.dataset_dict = self.create_dataset_dict(input, **kwargs)

    def open_intake_esm_catalogue(self, catfile, **kwargs):
        """Function to open an intake-sm catalogue"""

        def write_to_gl_attrs(dataset_dict):
            return dataset_dict
            
        cat = intake.open_esm_datastore(catfile)
        if kwargs: cat = cat.search(**kwargs)
        with dask.config.set(**{'array.slicing.split_large_chuncks': False}):
            dataset_dict =  cat.to_dataset_dict(cdf_kwargs = {"use_cftime": True, "decode_timedelta": False, "chunks": {}})
        return write_to_gl_attrs(dataset_dict)

    def open_xrdataset(self, files, use_cftime=True, parallel=True, data_vars='minimal', chunks={'time':1}, 
                       coords='minimal', compat='override', drop=None, **kwargs):
        """optimized function for opening large cf datasets.

        based on https://github.com/pydata/xarray/issues/1385#issuecomment-561920115

        decode_timedelta=False is added to leave variables and coordinates with time units in 
        {“days”, “hours”, “minutes”, “seconds”, “milliseconds”, “microseconds”} encoded as numbers.
    
        """
        def drop_all_coords(ds):
            return ds.reset_coords(drop=True)

        ds = xr.open_mfdataset(files, parallel=parallel, decode_times=False, combine='by_coords', 
                               preprocess=drop_all_coords, decode_cf=False, chunks=chunks,
                               data_vars=data_vars, coords=coords, compat=compat, **kwargs)

        return xr.decode_cf(ds, use_cftime=use_cftime, decode_timedelta=False)

    def create_input_dictionary(self, input, **kwargs):
        """Function to create xarray dataset dictionary from input"""

        def _create_filelist(input_lst):
            file_lst = []
            for ifile in input:
                if os.path.isfile(ifile):
                    file_lst.append(ifile)
                elif os.path.isdir(ifile):
                    file_lst+=glob.glob(ifile + '/*')
                else:
                    warnings.warn( 'Could not find input file(s) {}.'.format(ifile))
            return file_lst

        def _get_input_dict(iname, ifiles, **kwargs):
            inputdict = {}
            try:
                inputdict[iname] = self.open_xrdataset(ifiles, **kwargs)
                return inputdict
            except:
                pass
            
            for ifile in ifiles:
                try:
                    inputdict[ifile] = self.open_xrdataset(ifile, **kwargs)
                    continue
                except:
                    pass
                try:
                    inputdict.update(self.open_intake_esm_catalogue(ifile, **kwargs))
                    continue
                except:
                    warnings.warn('Input file {} has no valid file format. Use netCDF files or intake-esm catalogues.'.format(ifile))
            return inputdict

        files = _create_filelist(input)
    
        return _get_input_dict(input[0], files, **kwargs)


    def identify_input_format(self, input, **kwargs):
        """Function to identify input file format"""
        if isinstance(input, str): 
            input = [input]
        if isinstance(input, list):
            inputdict = self.create_input_dictionary(input, **kwargs)
        if isinstance(input, dict):
            inputdict = input
        return inputdict

    def create_dataset_dict(self, input, **kwargs):
        """Returns xarray dataset dictionary"""
        inputdict = self.identify_input_format(input, **kwargs)
        if not inputdict:
            raise IndexError ('Empty file dictionary')
        for name, ds in inputdict.items():
            ds.attrs['vars'] = get_variable_name(ds)
            inputdict[name] = ds
        return {create_newname(ds.vars,name) : ds for name, ds in inputdict.items()}
