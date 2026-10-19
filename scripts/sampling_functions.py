import xarray as xr
import numpy as np
import os
import pandas as pd
import pyproj

def compute_sic(left_x, right_x, lower_y, upper_y, sic_data):
    """Compute the sea ice extent as a fraction of total area within the region bounded
    by <left_x>, <right_x>, <bottom_y>, and <top_y> using the netcdf file <sic_data>. Assumes
    that sic_data is the NSIDC SIC CDR.
    """
    x_idx = (sic_data.x >= left_x) & (sic_data.x <= right_x)
    y_idx = (sic_data.y >= lower_y) & (sic_data.y <= upper_y)
    
    with_ice = ((sic_data.sel(x=x_idx, y=y_idx)['cdr_seaice_conc'] > 0.15) & \
                (sic_data.sel(x=x_idx, y=y_idx)['cdr_seaice_conc'] <= 1))
    coast_mask = (sic_data.sel(x=x_idx, y=y_idx)['cdr_seaice_conc'] > 1).sum() 
    total_area_pixels = np.prod(with_ice.shape)
    sic_area_pixels = with_ice.sum().data
    sic_mean = (sic_data.sel(x=x_idx, y=y_idx).where(with_ice))['cdr_seaice_conc'].mean().data
    return {'sea_ice_fraction': np.round(sic_area_pixels/(total_area_pixels - coast_mask.data), 3),
            'mean_sea_ice_concentration': np.round(sic_mean, 3)}

def find_candidates(n_samples, region_info, dx, sic_path,
                    sif_threshold=0.25, margin=50, start_year=2003, end_year=2022,
                    min_samples_per_month=10):
    """Generate a list of candidate locations for the validation dataset. Initial samples were selected using the
    same steps as shown here. This function places the steps in one place for convenience, and implements a correction
    to the SIC calculation used in the initial version.
    
    n: sets the number of candidates to generate.
    region_info: a row from the region_definitions table. Must include start_doy and end_doy.
    dx is the dimension in km of the sample scene.
    sic_path: path to folder with the NSIDC CDR data.
    sif_threshold: between 0 and 1. The ice fraction needed to retain a sample.
    margin: distance in km that the center needs to be from the edge of the region boundary.
    """
    dx_meters = dx*1e3
    margin_meters = margin * 1e3
    region = region_info.name
    start_doy = region_info.start_doy
    end_doy = region_info.end_doy
    left_x = region_info.left_x
    right_x = region_info.right_x
    lower_y = region_info.lower_y
    upper_y = region_info.upper_y

    # calculations are done in polar stereographic
    # use pyproj to convert back to lon/lat for final table
    crs0 = pyproj.CRS('WGS84')
    crs1 = pyproj.CRS('epsg:3413')
    transformer_ll = pyproj.Transformer.from_crs(crs1, crs_to=crs0, always_xy=True)
    
    # we keep track of the number of samples generated per month
    # the range is set up this way so that we don't get extra months in 
    # leap years. For other uses the start and end doy could be adjusted differently.
    start_month = (pd.to_datetime('2000-01-01') + pd.to_timedelta(start_doy, unit='d')).month
    end_month = (pd.to_datetime('2000-01-01') + pd.to_timedelta(end_doy - 1, unit='d')).month
    samples_by_month = pd.Series(0, index=np.arange(start_month, end_month+1))
    candidates = []
    
    def in_box(x, y, margin_meters):
        """Convenience function that checks whether point x, y is in region.
        Returns True if x, y in the box."""
        if left_x <= x - margin_meters:
            if right_x >= x + margin_meters:
                if lower_y <= y - margin_meters:
                    if upper_y >= y + margin_meters:
                        return True
        return False
    
    while np.any(samples_by_month < min_samples_per_month):
        # Randomly select date from months with not enough samples
        year = np.random.choice(np.arange(start_year, end_year+1))
        remaining_months = list(samples_by_month[samples_by_month < min_samples_per_month].index)
        month = np.random.choice(remaining_months)
        days_in_month = pd.to_datetime(str(year) + '-' + str(month) + '-01').daysinmonth
        day = np.random.choice(np.arange(1, days_in_month+1))
        date = str(year) + str(month).zfill(2) + str(day).zfill(2)
        
        # Load SIC data for the date. If any MIZ regions, randomly select center point
        # with sea ice concentration between 15 and 85 percent, otherwise pass    
        min_ice = 0.15
        max_ice = 0.85
        
        files = os.listdir(sic_path + str(year))
        f = next(f for f in files if date in f)
            
        with xr.open_dataset(sic_path + str(year) + '/' + f) as sic_data:
            # generate center point
            X, Y = np.meshgrid(sic_data.x, sic_data.y)
            miz = (sic_data['cdr_seaice_conc'] >= min_ice) & (sic_data['cdr_seaice_conc'] <= max_ice)
            miz = np.ravel(miz.squeeze())
            xoptions = np.ravel(X)[miz]
            yoptions = np.ravel(Y)[miz]
            inside = np.array([in_box(x, y, margin_meters) for x, y in zip(xoptions, yoptions)])
    
            if np.any(inside):
                ii = np.random.choice(np.arange(len(xoptions))[inside])
                
                # get x, y coordinates
                x0 = xoptions[ii]
                y0 = yoptions[ii]

                # define scene centered at x0, y0
                left_x0 = x0 - dx_meters/2
                right_x0 = x0 + dx_meters/2
                lower_y0 = y0 - dx_meters/2
                upper_y0 = y0 + dx_meters/2
                
                sic_results = compute_sic(left_x0, right_x0, lower_y0, upper_y0, sic_data)
                # check SIF threshold
                if sic_results['sea_ice_fraction'] >= sif_threshold:
                    lon0, lat0 = transformer_ll.transform(x0, y0)
                    candidates.append([region, pd.to_datetime(date).strftime('%Y-%m-%d'),
                                       lon0, lat0, x0, y0, sic_results['sea_ice_fraction'],
                                       sic_results['mean_sea_ice_concentration']])
                    samples_by_month[month] += 1

    candidates = pd.DataFrame(candidates,
            columns=['region', 'start_date', 'center_lon', 'center_lat',
                     'center_x', 'center_y', 'sea_ice_fraction', 'mean_sea_ice_concentration'])

    candidates['month'] = pd.to_datetime(candidates['start_date'].values).month
    return candidates