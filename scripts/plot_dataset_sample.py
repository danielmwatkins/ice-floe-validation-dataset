import numpy as np
import os
import pandas as pd
import ultraplot as pplt
import rasterio as rio
from rasterio.plot import reshape_as_image

# Load the list of cloud clearing evaluation cases
df = pd.read_csv('../data/validation_dataset/validation_dataset.csv')
df['case_number'] = [str(cn).zfill(3) for cn in df['case_number']]
df.groupby('region').count()
df['start_date'] = pd.to_datetime(df['start_date'].values)
df.index = [cn + '_' + sat for cn, sat in zip(df.case_number, df.satellite)]

def fname(case_data, imtype='labeled_floes'):
    """Generates filenames from rows in the overview table. imtype can be 'labeled_floes', 
    'binary_floes', 'binary_landfast', or 'binary_landmask', 'truecolor', or 'falsecolor'.
    The imtype determines whether a 'png' or 'tiff' is returned.
    """

    cn = case_data['case_number']
    date = pd.to_datetime(case_data['start_date']).strftime('%Y%m%d')
    region = case_data['region']
    sat = case_data['satellite']
    if 'binary' in imtype:
        return  '-'.join([cn, region, date, sat, imtype + '.png'])
        
    elif imtype in ['truecolor', 'falsecolor', 'cloudfraction', 'labeled_floes',]:
        prefix = '-'.join([cn, region, '100km', date])
        return '.'.join([prefix, sat, imtype, '250m', 'tiff'])

    elif imtype in ['seaice', 'landmask',]:
        prefix = '-'.join([cn, region, '100km', date])
        return '.'.join([prefix, 'masie', imtype, '250m', 'tiff'])     

    elif imtype == 'cloudfraction_numeric':
        
        return '-'.join([cn, region, date, sat, 'cloudfraction.csv'])

# Load raster data and masks
fc_dataloc = '../data/modis/falsecolor/'
tc_dataloc = '../data/modis/truecolor/'
cf_dataloc = '../data/modis/cloudfraction_numeric/'

lm_dataloc = '../data/validation_dataset/binary_landmask/'
lb_dataloc = '../data/validation_dataset/binary_floes/'
lf_dataloc = '../data/validation_dataset/binary_landfast/'

masie_ice_loc = '../data/masie/seaice/'
masie_land_loc = '../data/masie/landmask/'

tc_images = {}
fc_images = {}
cf_images = {}
lb_images = {}
lf_images = {}
lm_images = {}
mi_images = {}
ml_images = {}

missing = []
for row, data in df.iterrows():

    if data.case_number in ['011', '108', '022', '128']:
        
        for datadir, imtype, data_dict in zip([tc_dataloc, fc_dataloc, cf_dataloc,
                                               lb_dataloc, lf_dataloc, lm_dataloc,
                                               masie_ice_loc, masie_land_loc],
                                              ['truecolor', 'falsecolor', 'cloudfraction_numeric',
                                               'binary_floes', 'binary_landfast', 'binary_landmask',
                                               'seaice', 'landmask'],
                                              [tc_images, fc_images, cf_images,
                                               lb_images, lf_images, lm_images,
                                               mi_images, ml_images]):
            try:
                if imtype != 'cloudfraction_numeric':
                    with rio.open(datadir + fname(df.loc[row,:], imtype)) as im:
                        data_dict[row] = im.read()
                else:
                    data_dict[row] = pd.read_csv(
                        datadir + fname(df.loc[row,:], imtype), index_col=0) 
                    data_dict[row].index = data_dict[row].index.astype(int)
                    data_dict[row].columns = data_dict[row].columns.astype(int)
                    
            except:
                if imtype in ['falsecolor', 'cloudfraction_numeric', 'landmask']:
                    print('Couldn\'t read', fname(df.loc[row,:], imtype), imtype)
                elif imtype == 'binary_floes':
                    if df.loc[row, 'visible_floes'] == 'yes':
                        missing.append(fname(df.loc[row,:], imtype))
                elif imtype == 'binary_landfast':
                    if df.loc[row, 'visible_landfast_ice'] == 'yes':
                        missing.append(fname(df.loc[row,:], imtype))
                elif imtype in ['seaice', 'landmask']: # masie images
                    missing.append(fname(df.loc[row,:], imtype))

fig, ax = pplt.subplots(nrows=4, ncols=4, share=False)
titles = ['011 Baffin Bay', '022 Barents-Kara Seas', '108 Greenland Sea', '128 Hudson Bay']
for i, case in enumerate(['011', '022', '108', '128']):
    case_number = case + '_aqua'
    ax[0,i].imshow(reshape_as_image(tc_images[case_number]))
    ax[1,i].imshow(reshape_as_image(fc_images[case_number]))
    

        
    masie_ice = mi_images[case_number].squeeze()    
    ax[2,i].imshow(np.ma.masked_array(masie_ice, mask=masie_ice>0), c='blue2')
    
    # landmask
    binary_land = lm_images[case_number][0,:,:]
    ax[2,i].imshow(np.ma.masked_array(binary_land, mask=binary_land == 0), c='gray9')
    
    # labeled floes
    if case_number in lb_images:
        manual_ice = lb_images[case_number][0,:,:]
        ax[2,i].imshow(np.ma.masked_array(manual_ice, mask=manual_ice==0), c='red5')
        
    # labeled landfast
    if case_number in lf_images:
        manual_landfast = lf_images[case_number][0,:,:]
        ax[2,i].imshow(np.ma.masked_array(manual_landfast, mask=manual_landfast == 0), c='yellow4')


    c = ax[3,i].pcolormesh(cf_images[case_number].values, vmin=0, vmax=100, N=17, cmap='Blues_r')
    
    ax[3,i].format(yreverse=True)

h = []
for color in ['w', 'blue2', 'red5', 'yellow4', 'darkgray']:
    h.append(ax.plot([],[],m='s', lw=0, c=color, edgecolor='k'))

ax[2,-1].legend(h, ['Sea Ice (MASIE)', 'Water (MASIE)', 'Sea Ice Floes', 'Landfast Ice', 'Land'], loc='r', ncols=1)
    
ax[3,-1].colorbar(c, label='Cloud Fraction (%)')
fig.format(abc=True, xticks='none', yticks='none')
fig.format(toplabels=titles, leftlabels=['True Color (1-4-3)', 'False Color (7-2-1)','Validation Labels',  'Cloud Fraction (MODIS)'])
fig.save("../figures/fig_03_validation_dataset_sample.png", dpi=300)