import geopandas as gpd 
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import os
import rasterio

from importlib import reload 
from polyclean import polyclean
from rasterio.features import shapes, sieve
from rasterio.plot import reshape_as_image, reshape_as_raster
from shapely.geometry import Polygon
from shapely.ops import polygonize
from skimage.measure import label, regionprops
from skimage.segmentation import mark_boundaries, quickshift



# ------------------------------------------------------------------- #
#                          Filling holes                              #
# ------------------------------------------------------------------- #
# Data
aoi_file = '/Users/zach/Documents/GIS/data/vector/fill_holes/aoi_with_holes.gpkg'
aoi_holes_filled_file = '/Users/zach/Documents/GIS/data/vector/fill_holes/aoi_holes_filled.gpkg'
aoi_with_holes = gpd.read_file(aoi_file)
aoi_without_holes = gpd.read_file(aoi_holes_filled_file)

# Run it
aoi_holes_filled = polyclean.fill_holes(aoi_with_holes, 30000)
aoi_holes_filled.to_file('/Users/zach/Documents/GIS/data/vector/fill_holes/aoi_holes_filled_py_test.gpkg')

# Roads dataset
reload(polyclean)
roads_file = '/Users/zach/Documents/GIS/data/vector/corvallis/TransportationSHPs/TransportationSHPs\\RoadPoly.shp'
roads = gpd.read_file(roads_file)
potholes_fixed = polyclean.fill_holes(roads, 1e4)
potholes_fixed.to_file('/Users/zach/Documents/GIS/data/vector/corvallis/TransportationSHPs/Roads_potholes_filled.gpkg')


# ------------------------------------------------------------------- #
#                          Filling gaps                               #
# ------------------------------------------------------------------- #
reload(polyclean)
data = gpd.read_file('/Users/zach/Documents/GIS/data/vector/fill_gaps/layer_with_gaps.gpkg')
gaps_filled = polyclean.fill_gaps(data, eliminate=False)
gaps_filled.to_file('/Users/zach/Documents/GIS/data/vector/fill_gaps/gaps_filled.gpkg')


# ------------------------------------------------------------------- #
#                          Elimination                                #
# ------------------------------------------------------------------- #
reload(polyclean)
layer_with_gaps = gpd.read_file('/Users/zach/Documents/GIS/data/vector/fill_gaps/layer_with_gaps_2.gpkg')
polyclean.fill_gaps(layer_with_gaps, remove_gaps=False)
polyclean.fill_gaps(layer_with_gaps, remove_gaps=False).plot() ; plt.show()
gaps_eliminated_smol = polyclean.fill_gaps(layer_with_gaps)
gaps_eliminated_smol.reset_index(drop=True).to_file('/Users/zach/Documents/GIS/data/vector/fill_gaps/gaps_filled_eliminated.gpkg')


# ------------------------------------------------------------------- #
#                            Overlaps                                 #
# ------------------------------------------------------------------- #
reload(polyclean)
layer_dir = '/Users/zach/Documents/GIS/data/vector/overlaps'
overlaps = gpd.read_file(os.path.join(layer_dir, 'overlaps_smol.gpkg')).explode(index_parts=True)
# overlaps = gpd.read_file(os.path.join(layer_dir, 'ez_ovlp.gpkg'))
# Requires Shapely >= 1.8 --> use `polyclean` conda environment
# overlaps = gpd.GeoDataFrame(overlaps, geometry=[make_valid(x) for x in overlaps.geometry], crs=overlaps.crs)
overlaps.to_file(os.path.join(layer_dir, 'overlaps_valid.shp'))
ovlp_regions = polyclean.identify_overlaps(overlaps, flatten=False)
ovlp_regions.to_file(os.path.join(layer_dir, 'overlapping_regions.gpkg'))
flattened = polyclean.identify_overlaps(overlaps)
flattened.geom_type.unique()
# flattened.reset_index(drop=True).to_file(os.path.join(layer_dir, 'flattened.gpkg'))

flattened.reset_index(drop=True).to_file(os.path.join(layer_dir, 'flattened.shp'))

ovlps_eliminated = polyclean.eliminate(flattened, 'overlap')
ovlps_eliminated.reset_index(drop=True).to_file(os.path.join(layer_dir, 'eliminated.shp'))


# ------------------------------------------------------------------- #
#                 Overlaps: Wall-To-Wall Classified                   #
# ------------------------------------------------------------------- #
reload(polyclean)
layer_dir = '/Users/zach/Documents/GIS/data/raster'
out_dir = '/Users/zach/Documents/GIS/data/vector/overlaps/AK'
smoothed = gpd.read_file(os.path.join(layer_dir, 's2_median_rgb_sieved_reduced_polys_smoothed.gpkg')).to_crs(3338)
gaps_eliminated = polyclean.fill_gaps(smoothed)
gaps_eliminated.to_file(os.path.join(out_dir, 'gaps_eliminated.gpkg'))
ovlps = polyclean.identify_overlaps(gaps_eliminated, flatten=False)
ovlps.to_file(os.path.join(out_dir, 'overlapping_regions.gpkg'))
flattened = polyclean.identify_overlaps(smoothed, flatten=True)
flattened.reset_index(drop=True).to_file(os.path.join(out_dir, 'flattened.gpkg'))

# ------------------------------------------------------------------- #
#                          Bigger dataset                             #
# ------------------------------------------------------------------- #
reload(polyclean)

# Re-write the 14-band raster as RGB for size considerations
with rasterio.open('/Users/zach/Documents/GIS/data/raster/S2_vis_median-0000000000-0000026880.tif') as src:
    image_og = reshape_as_image(src.read(out_dtype='float32'))

# src.profile
attrs_rgb = {
    'driver': 'GTiff',
    'width': src.width,
    'height': src.height,
    'count': 3,
    'dtype': np.uint8,
    'crs': src.crs,
    'transform': src.transform
}
# Rescale to 0-255 8-bit
image = np.copy(image_og)
for band in range(1, 4):
    max_val = np.nanmax(image[:,:,band])
    min_val = np.nanmin(image[:,:,band])
    val_range = max_val - min_val
    image[:,:,band] = ((image[:,:,band]-min_val)*255) / val_range

np.nanmax(image[:,:,1]) ; np.nanmin(image[:,:,1])
np.nanmax(image[:,:,2]) ; np.nanmin(image[:,:,2])
np.nanmax(image[:,:,3]) ; np.nanmin(image[:,:,3])

# Sentinel-2 bands: 4-Red, 3-Green, 2-Blue
# raster = reshape_as_raster(image[:, :, 1:4])
raster = reshape_as_raster(image[:, :, (3,2,1)])
with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb.tif', 'w', **attrs_rgb) as src:
    src.write(raster)

with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb.tif') as src:
    im = reshape_as_image(src.read(out_dtype=np.uint8))   

# --------- Quickshift ------------ #
segmented = quickshift(im, kernel_size=3, max_dist=6, ratio=0.5)  # Takes about 3-4 minutes
im_with_boundaries = mark_boundaries(im, segmented)
plt.imshow(im_with_boundaries) ; plt.show()
with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_segments.tif', 'w', **attrs_rgb) as src:
    src.write(reshape_as_raster(im_with_boundaries))
# plt.imshow(segmented) ; plt.show()

with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_segments.tif') as src:
    segs = reshape_as_image(src.read())


# ------------ Labeling Points ----------- #
with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb.tif') as src:
    im = src.read(out_dtype=np.uint8, masked=True)
im_masked = ma.masked_equal(im, 0)
with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_masked.tif', 'w', **attrs_rgb) as src:
    src.write(im_masked)

# sieved = np.copy(im)
sieved = im_masked
for band in range(3):
    sieved[band, :, :] = sieve(im[band,:,:], 1000000)

plt.imshow(reshape_as_image(sieved)) ; plt.show()

with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved.tif', 'w', **attrs_rgb) as src:
    src.write(sieved)



# ------ 12.23.21: START HERE -------- #
with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced.tif') as src:
    sieved = reshape_as_image(src.read())

attrs_reduced = {
    'driver': 'GTiff',
    'width': src.width,
    'height': src.height,
    'count': 3,
    'dtype': np.uint8,
    'crs': src.crs,
    'transform': src.transform
}
segs = quickshift(sieved)
bounded = mark_boundaries(sieved, segs)
with rasterio.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced_segments.tif', 'w', **attrs_reduced) as dst:
    dst.write(reshape_as_raster(bounded))
labels = label(bounded, connectivity=2)
regions = regionprops(labels)  # only needed if sieving/eliminating

gen = shapes(segs.astype(np.uint16), connectivity=8, transform=src.transform)
poly_list = []
for shp in gen:
    poly_list.append(Polygon(shp[0]['coordinates'][0]))

gdf = gpd.GeoDataFrame(geometry=poly_list, crs=src.crs)
# gdf.plot() ; plt.show()
gdf.to_file('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced_polys.gpkg')

reload(polyclean)
import fiona
with fiona.open('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced_polys.gpkg') as src:
    # smoothed = src.items()
    props = src.profile
    schema = src.schema
    obj = next(iter(src))
    print(obj['geometry']['coordinates'][0])

smoothed = gpd.read_file('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced_polys_smoothed.gpkg')
gaps_filled = polyclean.fill_gaps(smoothed.to_crs(3857), remove_gaps=False)
gaps_filled.to_file('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced_polys_smoothed_gapfill.gpkg')
gaps_filled = gpd.read_file('/Users/zach/Documents/GIS/data/raster/s2_median_rgb_sieved_reduced_polys_smoothed_gapfill.gpkg')
gaps_eliminated = polyclean.fill_gaps(smoothed.to_crs(3857))
gaps_eliminated.plot() ; plt.show()
gaps_eliminated.to_file('/Users/zach/Documents/GIS/data/raster/93_eliminated.gpkg')

data = gaps_filled