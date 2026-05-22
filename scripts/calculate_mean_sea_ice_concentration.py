"""Compute mean sea ice concentration for each month from the NSIDC CDR v5 for use in 
plotting the study regions.
"""

import xarray as xr
import numpy as np
import os
import pandas as pd
import pyproj

# Location of monthly SIC files
sic_dataloc = '' # Add path to location where monthly NSIDC CDR 5 files have been downloaded 

files = os.listdir(sic_dataloc)
files = [f for f in files if '_2' in f]
files.sort()
dates = [pd.to_datetime(f.split('_')[2], format='%Y%m') for f in files]

month_data = {}
for month in [4, 9]:
    temp = []
    for file, date in zip(files, dates):
        if date.month == month:
            with xr.open_dataset(os.path.join(sic_dataloc,file)) as ds:
                temp.append(ds)
    month_data[month] = xr.concat(temp, dim='time', data_vars='all').mean(dim='time')

# Passive microwave SIC has a bias in summer where bright, warm coastal water
# gets flagged as sea ice. This section applies a mask to these regions.

x = month_data[9].x
y = month_data[9].y
X, Y = np.meshgrid(x, y)
transformer_ll = pyproj.Transformer.from_crs(pyproj.CRS('epsg:3413'),
                                             crs_to=pyproj.CRS('WGS84'),
                                             always_xy=True)
lons, lats = transformer_ll.transform(X,  Y)
idx_mask = (lats < 75) & ((lons >= 0) & (lons < 160))
idx_mask = idx_mask | ((lats < 70) & (lons > 160))
idx_mask = idx_mask | ((lats < 70) & (lons < -160))
idx_mask = idx_mask | ((lats < 75) & ((lons > -90) & (lons <= -30)))
month_data[9]['cdr_seaice_conc_monthly'] = month_data[9]['cdr_seaice_conc_monthly'].where(~idx_mask)

# save results
for month, name in zip([4, 9], ['april', 'september']):
    ds = month_data[month]
    ds.encoding = {'source': 'NSIDC CDR v5'}
    ds.to_netcdf('../data/nsidc/mean_sic_{n}_2000-2024.nc'.format(n=name))