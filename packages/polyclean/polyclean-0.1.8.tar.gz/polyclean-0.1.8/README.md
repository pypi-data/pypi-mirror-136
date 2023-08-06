# polyclean
Clean up geospatial polygon datasets.

This package provides utilities for cleaning up messy polygon data in geospatial datasets. It aims to provide solutions to common issues such as holes, gaps, and overlaps. Generally, functions expect a `geopandas.GeoDataFrame` as input and will return one as well. Polygons are thus always passed around as data frames, making it easy to translate them to and from commonly used geospatial file formats (e.g. OGC GeoPackage, ESRI Shapefile). This has the added benefit of mimicking the way vector workflows are done in QGIS or ArcGIS, making the package more intuitive to use (hopefully).

This package relies heavily on [`Geopandas`](https://geopandas.org/en/stable/) and [`Shapely`](https://shapely.readthedocs.io/en/stable/), so understanding how those packages handle vector data will aid with understanding `polyclean` utilities.

## Installation
### UNIX-like (Linux, MacOS)

`pip install polyclean`

This should install the package and all necessary dependencies.

### Windows
Make sure you have the following packages installed *first*:

- `Fiona`
- `GDAL`

Any recent version (compatible with `Shapely > 0.10`) should suffice. 

## Examples
### Fill Holes
Holes in polygons can be filled in based on area. To fill in all holes in a dataset, set the `threshold` value to a very large value (e.g. `1e6`).

![holes_examplepng](https://user-images.githubusercontent.com/8603349/147906975-a8fee143-5809-4997-b622-eff2fc622f90.png)

### Fill Gaps
Gaps between polygons can be identified and eliminated. A new field called `gap` is created, with gap polygons given a value of 1 and non-gap polygons (i.e. the original polygons) given the value `NaN`. These gaps can be automatically removed by folding them into the polygon with which they share the longest edge. This mimics the functionality of the the [ArcGIS Eliminate tool](https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/eliminate.htm).

<img width="637" alt="combined" src="https://user-images.githubusercontent.com/8603349/147909181-af731d27-fba2-49aa-bfc6-30e4f311d724.png">

