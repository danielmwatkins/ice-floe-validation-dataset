import pandas as pd
import ultraplot as uplt
import cartopy.crs as ccrs
import numpy as np
import warnings
import xarray as xr
import pyproj
import os

warnings.simplefilter('ignore')

uplt.rc['reso'] = 'med'
uplt.rc['cartopy.circular'] = False

# Load SIC mean data
ds_april_mean = xr.open_dataset('../data/nsidc/mean_sic_april_2000-2024.nc')
ds_sept_mean = xr.open_dataset('../data/nsidc/mean_sic_september_2000-2024.nc')
X = ds_april_mean.x
Y = ds_sept_mean.y

# Load region data
regions = pd.read_csv('../data/metadata/region_definitions.csv', index_col=0)
regions['print_title'] = [c.replace('_', ' ').title().replace('Of', 'of') for c in regions.index]

# Put in longitude order starting with Greenland
regions = regions.loc[['greenland_sea',
                       'barents_kara_seas',
                       'laptev_sea',
                       'sea_of_okhostk',
                       'east_siberian_sea',
                       'bering_chukchi_seas',
                       'beaufort_sea',
                       'hudson_bay',
                       'baffin_bay'],:]


crs = ccrs.NorthPolarStereo(central_longitude=-45, true_scale_latitude=70)
fig, ax = uplt.subplots(width=4.5, proj='npstere', proj_kw={'lon_0': -45})
ax.format(land=True, color='k', boundinglat=52, landzorder=0, latmax=90, facecolor='w', lonlocator=10)
ax.set_extent([-3.5e6, 2.8e6, -4e6, 4.4e6], crs=crs)

for region in regions.index:
    xbox = np.array([regions.loc[region, coord] for coord in ['left_x', 'left_x', 'right_x', 'right_x', 'left_x']])
    ybox = np.array([regions.loc[region, coord] for coord in ['lower_y', 'upper_y', 'upper_y', 'lower_y', 'lower_y']])
    ax.plot(xbox, ybox, transform=crs, lw=2, color='pink5')

miz = (ds_april_mean['cdr_seaice_conc_monthly'] > 0.15) & \
            (ds_april_mean['cdr_seaice_conc_monthly'] < 0.85)
april_miz = np.ma.masked_array(np.ones(miz.data.shape), mask=~miz)    

miz = (ds_sept_mean['cdr_seaice_conc_monthly'] > 0.15) &  \
            (ds_sept_mean['cdr_seaice_conc_monthly'] < 0.85)
sept_miz = np.ma.masked_array(np.ones(miz.data.shape), mask=~miz)    

apr_pack_ice = (ds_april_mean['cdr_seaice_conc_monthly'] >= 0.85) & \
            (ds_april_mean['cdr_seaice_conc_monthly'] <= 1)
apr_pack_ice = np.ma.masked_array(np.ones(apr_pack_ice.data.shape), mask=~apr_pack_ice)    

sep_pack_ice = (ds_sept_mean['cdr_seaice_conc_monthly'] >= 0.85) & \
            (ds_sept_mean['cdr_seaice_conc_monthly'] <= 1)

sep_pack_ice = np.ma.masked_array(np.ones(sep_pack_ice.data.shape), mask=~sep_pack_ice)    


ax.pcolormesh(X, Y, apr_pack_ice, vmin=0, vmax=1, color='blue1', alpha=1,
              transform=crs, label='')
ax.pcolormesh(X, Y, april_miz, vmin=0, vmax=1, color='blue4', alpha=1,
              transform=crs, label='')
ax.pcolormesh(X, Y, sep_pack_ice, vmin=0, vmax=1, color='orange1', alpha=1,
              transform=crs, label='')
ax.pcolormesh(X, Y, sept_miz, vmin=0, vmax=1, color='orange3', alpha=1,
              transform=crs, label='September MIZ')

h = [ax.plot([],[],marker='s', lw=0, color=color) for color in ['blue4', 'blue1', 'orange3', 'orange1']]
ax.legend(h, ['April MIZ', 'April Pack Ice', 'September MIZ', 'September Pack Ice'], loc='ur', ncols=1, alpha=1)
idx = 1
for region in regions.index:
    ax.text(regions.loc[region, 'left_x'] + 300e3,
            regions.loc[region, 'upper_y'] - 400e3, str(idx),
            transform=crs, bbox=True, bboxalpha=1,
            border=False, color='k', borderwidth=0,
            bboxstyle='circle', bboxcolor='w', zorder=10)
    idx += 1
ax.text(100, 69, 'Arctic Circle', color='lightgray', transform=ccrs.PlateCarree(), rotation=-40)

ax.plot(np.linspace(0, 360, 100), np.ones(100)*66.3, ls='-.', color='light gray')
fig.save('../figures/fig_01_sample_locations_map.png', dpi=300)