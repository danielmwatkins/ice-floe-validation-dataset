# Ice Floe Validation Dataset: To-do items and notes


## Reviewing test images
* 003 - needs landfast ice mask
* 011 - MODIS cloud fraction is wrong (likely edge case -- image is clear)
* 014 - potentially issue with modis mask -- top left looks good, if any clouds are in other sections then they are essentially transparent
* 018 - ambiguous. Possibly transparent clouds, or issue with mask. Nearly clear.
* 021 - alignment with landmask and landfast ice
* 022 - major cloud shadow effects, but cloud fraction seems decent
* 042 - full image is cloudy, the MODIS mask is incorrect
* 059 - need landfast mask, even if no floes visible
* 061 - beautiful image
* 071 - another good example of where manual color thresholding could be used to get an ice/water mask
* 077 - MODIS mask appears agressive - possible transparent cloud or error.
* 088 - either transparent or MODIS error. Example of one where sea ice mask could be made, clouds are super thin.
* 096 - MODIS mask has a clear sky region, looks 100% cloudy to me
* 103 - are those floe labels right? doesn't look right
* 175 - MODIS mask has missing data, likely should be 100% all round
* 179 - possible edge effects, near-transparent clouds

## Add landfast ice masks even if no floes are visible
This will let us use the landfast ice to train the cloud model, and to test a post-processing routine for getting landfast ice cover. And it will let us remove landfast ice from the comparisons in the validation image.

## Labeling water
* The water mask is different than the other masks, in that I'm labeling regions that are confidently water rather than labeling all pixels. This distinction is noted in the naming scheme, as "binary_water_samples" rather than "masks".
* I started with getting water samples from each region, not every image with open water has been addressed yet.

