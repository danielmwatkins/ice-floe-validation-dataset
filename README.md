# ice floe validation dataset
The Ice Floe Validation Dataset is a collection of randomly sampled scenes spanning the circumpolar Arctic marginal ice zone.
The data set consists of 378 true color and false color MODIS images (189 scenes, with images from both \textit{Aqua} and \textit{Terra}) with corresponding binary masks of land, manually labeled sea ice floes, manually labeled landfast ice, and image metadata, randomly sampled from a wide range of locations and weather conditions. We also include MODIS cloud fraction data, regridded ice/water and land masks from the Multisensor Analysis of Sea Ice Extent (MASIE) 4-km product, and regridded sea ice concentration maps from the NSIDC/NOAA Climate Data Record of Sea Ice Concentration (v6, Meier et al. 2026) and the ARTIST Sea Ice Algorithm (Spreen et al., 2008).

## methods
Samples come from 9 regions shown in the figure and defined in the table below.
The large-scale bounding box for each region is defined using the center latitude and longitude with lateral (X,Y) dimensions in kilometers on the NSIDC North Polar Stereographic grid (EPSG 3413). Samples consist of 100 km by 100 km scenes centered on pixels with SIC between 15 and 85\%, with SIF $\geq 0.25$. Within each region, we identified the end of the spring-summer sea ice season by computing the climatology of sea ice fraction (SIF) for 2003-2022. The minimum sampling day of year (DOY) is set to 60 for all locations, while the maximum DOY is set to either day 273 or to the latest day on which the 90th percentile of SIF is greater than or equal to 0.5, whichever is earlier.

![Map of sample regions](./figures/fig_01_sample_locations_map.png)

|     | Center Latitude | Center Longitude |
| --- |  --- | --- |
| Greenland Sea	| 74.698 | -17.601 |
| Barents-Kara Seas	| 75.617 | 53.223 |
| Laptev Sea | 75.9228	| 124.689 |
| East Siberian Sea	| 75.171 | 165.192 |
| Bering Chukchi Seas| 65.596 | -169.076 |
| Beaufort Sea | 74.860	| -142.840 |
| Baffin Bay | 74.768 | -64.085 |
| Hudson Bay | 58.143 | -83.965 |
| Sea of Okhostk | 58.000 | 148.000 |

The SIF for each image was calculated separately using the SIC CDR and MASIE to avoid such cases.
Locations with high CDR SIF and low MASIE SIF were manually examined to determine whether sea ice was present.
Samples were drawn until sufficient cases were identified to draw 21 samples per region, stratified by month. 

![Sea ice fraction climatology](./figures/fig_02_sea_ice_fraction.png)


## dataset structure
The data directory has subdirectories

1. `/metadata` containing specification/config files
2. `/modis` containing truecolor, falsecolor, landmask, and cloudfraction images. Landmask images have been converted from RGB to binary, where land=true and water=false.
   * `truecolor/`
   * `falsecolor/`
   * `landmask/`
   * `cloudfraction/`
4. `/masie` containing images from the MASIE 4 km data product, cropped and aligned with the MODIS projection via nearest-neighbors interpolation
5. `/asi` containing interpolated images of SIC from the 6.25 km resolution Artist algorithm (Spreen et al., 2008)
6. `/nsidc` containing interpolated images of SIC from the 25 km resolution NOAA/NSIDC Climate Data Record of Sea Ice Concentration (Meier et al., 20
7. `/validation_dataset` containing the binary PNG, labeled TIFF files, and Photoshop files. The subdirectories are
   * `binary_floes/`
   * `binary_landfast/`
   * `labeled_floes/`
   * `property_tables/`

The files all follow a strict, informative naming convention. Each scene is defined by a unique identifier with the format `NNN-region_name-100km-YYYYMMDD` where NNN is the zero-padded, three digit case number. 
1. MODIS images: `NNN-region_name-100km-YYYYMMDD.satellite_name.image_type.250m.tiff`. Each case specifies a date and location, and contains two satellite images (Aqua and Terra). MODIS image types are `cloudfraction` (RGB), `truecolor` (Bands 1-4-3), `falsecolor` (Bands 7-2-1), and `landmask`.
2. Sea ice extent and concentration images: `NNN-region_name-100km-YYYYMMDD.product.image_type.250m.tiff` have `masie`, `asi`, or `nsidc` and have image types `sea_ice_concentration` (ASI, NSIDC), `sea_ice_extent` (MASIE) and `landmask`.
3. Validation images: `NNN-region_name-YYYYMMDD-satellite-image_type.file_type`. Image types with file type `png` are `binary_floes` and `binary_landfast`. Labeled floe masks are `tiff` with image type `labeled_floes` and have integer labels corresponding to the labels in the property tables.

Finally, the `/property_tables` contains the main metadata table with all case information and manual image assessments `ice_floe_validation_dataset.csv` as well as automatically generated property tables for each image with ice floes in it, and a table of hybrid automatic/manual floe matching for paired analyses. Passtimes for each image identified using the Satellite Overpass Identification Tool and NASA Earthdata Worldview are included.

## notebooks

1. `bookkeeping.ipynb` Scripts and diagnostics to check the completeness of the datasets.
2. `sample_selection.ipynb` Code for iterative random sampling

## scripts

1. `setup_locations.py`
2. `calculate_sea_ice_fraction.py`
3. `binarize_landmasks.py`
4. `extract_features_and_pair_floes.py`
5. `plot_locations.py`
6. `plot_sif_climatology.py`

## figures
The figures directory has diagnostic and explanatory figures, including the sea ice fraction climatology, the map of analyzed cases, and a summary of the metadata.

# citation
The dataset will be described in an upcoming paper in _IEEE Transactions on Geoscience and Remote Sensing_ "Automated segmentation and tracking of sea ice floes from optical remote sensing imagery with IceFloeTracker.jl". If you use the dataset in your work, please cite the dataset as

Watkins, D.M. and Wilhelmus M.M. (2026) "Ice Floe Validation Dataset", Zenodo, [doi: 10.5281/zenodo.17716713](https://doi.org/10.5281/zenodo.17716713)

The Zenodo DOI will always link to the newest version of the dataset.

# acknowledgments
Creation of the dataset was supported by grants from NASA and the US Office of Naval Research, under the direction of Dr. Monica Wilhelmus [wilhelmuslab.me](https://wilhelmuslab.me). Contributors to the data validation and labeling include Ellen Buckley, Minki Kim, Emma Slaght, Ethan Register, and Ashfaq Ahmed.

We acknowledge the use of the NASA Worldview Snapshots tool for MODIS data access.

# version history
Initial sampling and image analysis began in Spring 2024. Sampling regions were defined using equal-area boxes. An initial set of samples were drawn from 2003-2022, using v4 of the NSIDC CDR, and used for Simon Hatcher’s batchelor’s thesis in engineering to test methods for validating the Ice Floe Tracker algorithm. During the analysis, we noted four issues in the approach: 

1. Some regions, such as Hudson Bay, contained large ocean areas outside the intended region.
2. Overlapping region boundaries resulted in ambiguous region membership for samples.
3. Cases where the sample came from narrow channels which were smaller than the coastal buffer used in Ice Floe Tracker.
4. We identified multiple cases where the MODIS data was corrupted or missing, necessitating drawing more samples.
   
To address problem (1) and (2), we refined the region definitions to match the definitions from the International Hydrological Organization. We discarded samples which no longer belonged to any region. Then, we developed a sampling procedure to draw new samples such that all Marginal Ice Zone (MIZ) areas in the new sample had uniform likelihood of selection. The procedure is as follows. Consider a region $X$  and a new, overlapping region $Y$. We posses a sample of $n_X$ points from region $X$  and wish to form a sample of equal size from $Y$. Given a random sample of $m$ points from $Y$, we can separate them into $m_{Y\cap X}$  points from $Y \cap X$ (i.e., the points in $X$ that are also in $Y$ ), and $m_{Y\setminus X}$ points that are in the region of $Y$ but not in $X$. We determined the proportion $p$ of the original points to keep as  $p = m_{Y\cap X }/m$,  then based on these calculations, we randomly selected points to keep from the original sample and drew additional samples to bring the number of samples up to the original number. 

To address problem (3), we computed the ocean area remaining after landmask buffering and rejected samples with too little ocean coverage. Problem (4) simply required drawing more samples until we found samples with complete imagery. In most cases, this only required drawing one more sample. Manual labeling and metadata categorization continued over the next year.

In Spring 2025, we identified an issue with late-summer samples: erroneous high sea ice concentration in coastal waters in the NSIDC sea ice concentration dataset (Meier et al. 2021). To address this, we accessed MASIE data for comparison. This data first became available in 2006, so we restricted the samples to 2006 and onward. The MASIE dataset enabled us to flag where there were large discrepancies between estimated sea ice fraction in the NSIDC dataset and the MASIE ice extent. While the ice extent in MASIE still didn’t match perfectly with visual analysis, it did help us identify cases where insufficient sea ice was present. We drew additional samples to replace samples dropped by the the shifted time window, and continued working on manual floe labeling.

During Fall 2026, we performed a major overhaul of the dataset to address the need for a rigorous set of point samples for calibrating the Ice Floe Tracker classifier function. In addition, we found it necessary to expand the sample to include 500 km by 500 km images. These images were drawn as a superset of the 100 km images, starting from identifying the region centered at the original 100 km sample, then aligning the bounds to stay within the bounding boxes for the regions as necessary. 

The NSIDC Climate Data Record of Sea Ice was updated to Version 6. Re-running the sea ice fraction analysis, we found that the end date for the Sea of Okhostk occurs earlier in the season (June 9th, rather than June 22nd). This date is earlier than the dates for two of the samples: cases 171 and 173. We also noticed cases where the 100 km samples were not fully within the region boundaries due to insufficient buffering when drawing center location samples. In total, 9 cases were re-drawn. We updated the data format for the landmasks, and we add the ASI and NSIDC sea ice concentration data as grayscale images for all cases.

# references

1. Hatcher, S. (2024) “Error quantification in the Ice Floe Tracker algorithm.” Honors Batchelor’s Thesis, School of Engineering, Brown University
2. Meier, W., Fetterer, F., Windnagel, A., Stewart, J. S., & Stafford, T. (2026). NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6 [Data set]. National Snow and Ice Data Center. https://doi.org/10.7265/B18J-Z797
3. Spreen, G., Kaleschke, L., & Heygster, G. (2008). Sea ice remote sensing using AMSR-E 89-GHz channels. Journal of Geophysical Research: Oceans, 113(2), 1–14. https://doi.org/10.1029/2005JC003384

# generating the readme
The PDF version of the README is produced using `pandoc` via the commmand

```pandoc -s -V geometry:margin=1in -o README.pdf README.md```