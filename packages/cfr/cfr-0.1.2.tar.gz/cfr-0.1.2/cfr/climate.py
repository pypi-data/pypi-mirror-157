from datetime import datetime
import xarray as xr
import pandas as pd
import numpy as np
import copy
from tqdm import tqdm
from . import visual
from . import utils


class ClimateField:
    ''' The class for the gridded climate field data.
    
    Args:
        da (xarray.DataArray): the gridded data array.
        time_name (str): the name of the time dimension.
        lat_name (str): the name of the latitude dimension.
        lon_name (str): the name of the longitude dimension.
    
    '''
    def __init__(self, da=None, time_name=None, lat_name=None, lon_name=None):
        self.da = da
        if self.da is not None:
            self.refresh(time_name=time_name, lat_name=lat_name, lon_name=lon_name)

    def __getitem__(self, key):
        new = self.copy()
        new.da = new.da[key]
        if type(key) is tuple:
            new.time = new.time[key[0]]
        else:
            new.time = new.time[key]
        return new

    def refresh(self, time_name='time', lat_name='lat', lon_name='lon'):
        self.lat = self.da[lat_name].values
        self.lon = self.da[lon_name].values
        if time_name == 'year':
            self.time = self.da[time_name].values
        elif time_name == 'time':
            self.time = utils.datetime2year_float(self.da[time_name].values)
        else:
            raise ValueError('Wrong time_name; should be either "time" or "year".')

        self.vn = self.da.name
        self.lon_name = lon_name
        self.lat_name = lat_name
        self.time_name = time_name
        try:
            self.unit = self.da.attrs['units']
        except:
            self.unit = None

    def wrap_lon(self, mode='360', time_name='time', lon_name='lon'):
        if mode == '360':
            tmp_da = self.da.assign_coords({lon_name: np.mod(self.da[lon_name], 360)})
        elif mode == '180':
            tmp_da = self.da.assign_coords({lon_name: ((self.da[lon_name]+180) % 360)-180})
        else:
            raise ValueError('Wrong mode. Should be either "360" or "180".')

        tmp_da = tmp_da.sortby(tmp_da[self.lon_name])
        new = ClimateField().from_da(tmp_da, time_name=time_name)
        return new

    def from_da(self, da, time_name='time', lat_name='lat', lon_name='lon'):
        new = self.copy()
        new.da = da
        new.refresh(time_name=time_name, lat_name=lat_name, lon_name=lon_name)
        return new

    def from_np(self, time, lat, lon, value, time_name='time', lat_name='lat', lon_name='lon', value_name='tas'):
        new = self.copy()
        lat_da = xr.DataArray(lat, dims=[lat_name], coords={lat_name: lat})
        lon_da = xr.DataArray(lon, dims=[lon_name], coords={lon_name: lon})
        time_da = utils.year_float2datetime(time)
        da = xr.DataArray(
            value, dims=[time_name, lat_name, lon_name],
            coords={time_name: time_da, lat_name: lat_da, lon_name: lon_da},
            name=value_name,
        )
        new.da = da
        new.refresh(time_name=time_name, lat_name=lat_name, lon_name=lon_name)
        return new

    def get_anom(self, ref_period=[1951, 1980]):
        new = self.copy()

        if ref_period is not None:
            if ref_period[0] > np.max(self.time) or ref_period[-1] < np.min(self.time):
                utils.p_warning(f'>>> The time axis does not overlap with the reference period {ref_period}; use its own time period as reference [{np.min(self.time):.2f}, {np.max(self.time):.2f}].')
                var_ref = self.da
            else:
                var_ref = self.da.loc[str(ref_period[0]):str(ref_period[-1])]

            clim = var_ref.groupby('time.month').mean('time')
            new.da = self.da.groupby('time.month') - clim

        return new

    def center(self, ref_period=[1951, 1980], time_name='time'):
        new = self.copy()

        if ref_period is not None:
            if ref_period[0] > np.max(self.time) or ref_period[-1] < np.min(self.time):
                utils.p_warning(f'>>> The time axis does not overlap with the reference period {ref_period}; use its own time period as reference [{np.min(self.time):.2f}, {np.max(self.time):.2f}].')
                var_ref = self.da
            else:
                var_ref = self.da.loc[str(ref_period[0]):str(ref_period[-1])]

            clim = var_ref.mean(time_name)
            new.da = self.da - clim

        return new

    def load_nc(self, path, vn=None, time_name='time', lat_name='lat', lon_name='lon', load=False, **kwargs):
        if vn is None: 
            da = xr.open_dataarray(path, **kwargs)
        else:
            ds = xr.open_dataset(path, **kwargs)
            da = ds[vn]

        new = ClimateField(da=da, time_name=time_name, lat_name=lat_name, lon_name=lon_name)
        new = new.rename({lat_name: 'lat', lon_name: 'lon'})
        if load: new.da.load()
        return new

    def to_nc(self, path, verbose=True, **kwargs):
        self.da.to_netcdf(path, **kwargs)
        if verbose: utils.p_success(f'ClimateField saved to: {path}')

    def copy(self):
        return copy.deepcopy(self)

    def rename(self, new_vn):
        new = self.copy()
        new.da = self.da.rename(new_vn)
        new.vn = new_vn
        return new

    def __add__(self, fields):
        ''' Add a list of fields into the dataset
        '''
        new = ClimateDataset()
        new.fields[self.vn] = self.copy()
        if isinstance(fields, ClimateField):
            fields = [fields]

        if isinstance(fields, ClimateDataset):
            fields = [fields.fields[vn] for vn in fields.fields.keys()]

        for field in fields:
            new.fields[field.vn] = field

        new.refresh()
        return new

    def plot(self, it=0, **kwargs):
        try:
            t = self.da[self.time_name].values[it]
        except:
            t = self.da[self.time_name].values
            yyyy = str(t)[:4]
            mm = str(t)[5:7]
            t = datetime(year=int(yyyy), month=int(mm), day=1)

        if isinstance(t, np.datetime64):
            # convert to cftime.datetime
            t = utils.datetime2year_float([t])
            t = utils.year_float2datetime(t)[0]

        cbar_title = visual.make_lb(self.vn, self.unit)
        cmap_dict = {
            'tas': 'RdBu_r',
            'tos': 'RdBu_r',
            'pr': 'BrBG',
        }
        cmap = cmap_dict[self.vn] if self.vn in cmap_dict else 'viridis'
        if 'title' not in kwargs:
            if self.time_name == 'time':
                kwargs['title'] = f'{self.vn}, {t.year}-{t.month}' 
            elif self.time_name == 'year':
                kwargs['title'] = f'{self.vn}, {t}' 

        _kwargs = {
            'cbar_title': cbar_title,
            'cmap': cmap,
        }
        _kwargs.update(kwargs)
        if len(self.da.dims) == 3:
            fig, ax =  visual.plot_field_map(self.da.values[it], self.lat, self.lon, **_kwargs)
        elif len(self.da.dims) == 2:
            fig, ax =  visual.plot_field_map(self.da.values, self.lat, self.lon, **_kwargs)

        return fig, ax

    def annualize(self, months=list(range(1, 13))):
        new = self.copy()
        new.da = utils.annualize(da=self.da, months=months)
        new.time = np.floor(utils.datetime2year_float(new.da.time.values))
        return new

    def regrid(self, lats, lons, periodic_lon=False):
        new = self.copy()
        lat_da = xr.DataArray(lats, dims=[self.lat_name], coords={self.lat_name: lats})
        lon_da = xr.DataArray(lons, dims=[self.lon_name], coords={self.lon_name: lons})
        dai = self.da.interp(coords={self.lon_name: lon_da, self.lat_name: lat_da})
        if periodic_lon:
            dai[..., -1] = dai[..., 0]

        new.da = dai
        new.lat = dai[self.lat_name]
        new.lon = dai[self.lon_name]

        return new

    def crop(self, time_min=None, time_max=None, lat_min=None, lat_max=None, lon_min=None, lon_max=None):
        new = self.copy()
        if time_min is not None and time_max is not None:
            mask_time = (self.da[self.time_name] >= time_min) & (self.da[self.time_name] <= time_max)
        else:
            mask_time = None

        if lat_min is not None and lat_max is not None:
            mask_lat = (self.da[self.lat_name] >= lat_min) & (self.da[self.lat_name] <= lat_max)
        else:
            mask_lat = None

        if lon_min is not None and lon_max is not None:
            mask_lon = (self.da[self.lon_name] >= lon_min) & (self.da[self.lon_name] <= lon_max)
        else:
            mask_lon = None

        crop_dict = {}

        if mask_time is not None:
            crop_dict[self.time_name] = self.da[self.time_name][mask_time]

        if mask_lat is not None:
            crop_dict[self.lat_name] = self.da[self.lat_name][mask_lat]

        if mask_lon is not None:
            crop_dict[self.lon_name] = self.da[self.lon_name][mask_lon]

        dac = self.da.sel(crop_dict)
        new.da = dac
        new.refresh(time_name=self.time_name, lon_name=self.lon_name, lat_name=self.lat_name)

        return  new

    def geo_mean(self):
        wgts = np.cos(np.deg2rad(self.da[self.lat_name]))
        m = self.da.weighted(wgts).mean((self.lon_name, self.lat_name))
        return m

    def validate(self, fd_ref, stat='corr'):
        pass


class ClimateDataset:
    ''' The class for the gridded climate field dataset
    
    Args:
        fields (dict): the dictionary of :py:mod:`cfr.climate.ClimateField`
    
    '''
    def __init__(self, fields=None):
        self.fields = {} if fields is None else fields
        if fields is not None:
            self.refresh()

    def refresh(self):
        self.nv = len(list(self.fields.keys()))

    def copy(self):
        return copy.deepcopy(self)

    def load_nc(self, path, time_name='time', lat_name='lat', lon_name='lon', vn=None, load=False, **kwargs):
        new = self.copy()
        fields = {}
        ds = xr.open_dataset(path, **kwargs)
        if load: ds.load()
        if vn is None:
            for k in ds.variables.keys():
                if k not in [time_name, lat_name, lon_name]:
                    fields[k] = ClimateField(da=ds[k], time_name=time_name, lat_name=lat_name, lon_name=lon_name)
        else:
            fields[vn] = ClimateField(da=ds[vn], time_name=time_name, lat_name=lat_name, lon_name=lon_name)

        new.fields = fields
        new.nv = len(list(fields.keys()))
        return new

    def __add__(self, fields):
        ''' Add a list of fields into the dataset
        '''
        new = self.copy()
        if isinstance(fields, ClimateField):
            fields = [fields]

        if isinstance(fields, ClimateDataset):
            fields = [fields.fields[vn] for vn in fields.fields.keys()]

        for field in fields:
            new.fields[field.vn] = field

        new.refresh()
        return new

    def __sub__(self, fields):
        ''' Add a list of fields into the dataset
        '''
        new = self.copy()
        if isinstance(fields, ClimateField):
            fields = [fields]

        if isinstance(fields, ClimateDataset):
            fields = [fields.fields[vn] for vn in fields.fields.keys()]

        for field in fields:
            try:
                del new.fields[field.vn]
            except:
                utils.p_warning(f'>>> Subtracting {field.vn} failed.')

        new.refresh()
        return new

    def annualize(self, months=list(range(1, 13))):
        new = ClimateDataset()
        for vn, fd in tqdm(self.fields.items(), total=self.nv, desc='Annualizing ClimateField'):
            sfd = fd.annualize(months=months)
            new += sfd

        new.refresh()
        return new

    def get_anom(self, ref_period=[1951, 1980]):
        new = ClimateDataset()
        for vn, fd in tqdm(self.fields.items(), total=self.nv, desc='Getting anomaly from ClimateField'):
            sfd = fd.get_anom(ref_period=ref_period)
            new += sfd
        new.refresh()
        return new

    def center(self, ref_period=[1951, 1980]):
        new = ClimateDataset()
        for vn, fd in tqdm(self.fields.items(), total=self.nv, desc='Getting anomaly from ClimateField'):
            sfd = fd.center(ref_period=ref_period)
            new += sfd
        new.refresh()
        return new

    def from_ds(self, ds, time_name='time', lat_name='lat', lon_name='lon'):
        ''' Get data from the Xarray.Dataset object
        '''
        new = self.copy()
        fields = {}
        for k in ds.variables.keys():
            if k not in ['time', 'lat', 'lon']:
                fields[k] = ClimateField(da=ds[k], time_name=time_name, lat_name=lat_name, lon_name=lon_name)

        new.fields = fields
        return new

    def regrid(self, lat, lon):
        lat_da = xr.DataArray(lat, dims=['lat'], coords={'lat': lat})
        lon_da = xr.DataArray(lon, dims=['lon'], coords={'lon': lon})
        dsi = self.ds.interp(lon=lon_da, lat=lat_da)
        new = self.from_ds(dsi)

        return new