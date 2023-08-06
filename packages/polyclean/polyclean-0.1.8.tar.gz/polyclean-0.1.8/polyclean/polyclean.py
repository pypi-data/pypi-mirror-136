"""polyclean.py

Functions for cleaning and QCing vector data.

- Fill holes inside polygons
- Identify and eliminate gaps between polygons
- TODO: Remove overlaps between polygons 
- TODO: Resolve self intersections
"""

import geopandas as gpd
import operator

from shapely.geometry import Polygon
from shapely.ops import unary_union
from tqdm import tqdm
from warnings import warn


def eliminate(data: gpd.GeoDataFrame, field: str):
    """Eliminates specified polygons.

    Each tagged polygon is merged into the neighboring polygon with 
    which it has a longest shared edge.
    
    Parameters
    ----------
    data : gpd.GeoDataFrame

    field : str
        The field to eliminate on. Features that aren't to be eliminated
        should be coded as NaN.

    Returns
    -------
    gpd.GeoDataFrame
    """
    to_eliminate = data[data[field].notna()]
    for feature in tqdm(to_eliminate.geometry):
        # Find which (non-elimination eligible) polygon it shares the 
        # longest border with.
        parent_polys = [x for x in data[data[field].isna()].geometry if feature.intersects(x)]
        edges = {feature.intersection(pp).length: pp for pp in parent_polys}

        try:
            lse_poly = max(edges.items(), key=operator.itemgetter(0))[1]
        except ValueError:
            warn('No longest edge found for feature. Skipping...')
            continue

        # Merge (eliminate) the feature with the feature it shares the
        # longest edge with.
        merged = feature.union(lse_poly)
        if merged.geom_type != 'Polygon':
            merged = merged.buffer(0)  # Try 0-buffer trick to turn geometry collections into polygons.
        data.loc[data.geometry==lse_poly, 'geometry'] = merged

    eliminated = data[data[field].isna()]

    return eliminated


def fill_gaps(data, remove_gaps=True):
    """Fill gaps between polygons.
    
    Parameters
    ----------
    data : gpd.GeoDataFrame

    remove_gaps : bool
        Whether or not to eliminate the gaps by longest shared edge.

    Returns
    gpd.GeoDataFrame
    """
    if any(data.geom_type != 'Polygon'):
        warn('Multipart polygons detected. Exploding...')
        data = data.explode(index_parts=True)

    # Set geometry precision to prevent rounding artifiacts.
    data = _round_geometries(data)
    data_boundary = _round_geometries(_fill_boundary(data))
    
    print('Identifying gaps...')
    gaps = (data_boundary
        .overlay(data, how='difference', keep_geom_type=True)
        .explode(index_parts=False)
    )
    gaps['gap'] = 1
    gaps['gap_area'] = round(gaps.area, 3)

    gaps_filled = data.append(gaps)

    if remove_gaps:
        print('Eliminating gaps by longest shared edge...')
        gaps_filled = eliminate(gaps_filled, 'gap')

    return gaps_filled


def fill_holes(data, threshold):
    """Fill holes by area.
    
    Parameters
    ----------
    data : gpd.GeoDataFrame
    
    threshold : float
        Area threshold below which holes will be filled.
    
    Returns
    -------
    gpd.GeoDataFrame
    """
    print('Filling holes...')

    if 'MultiPolygon' in data.geom_type.unique():
        data = data.explode(index_parts=True)

    polys_updated = []
    for feature in data.geometry:
        interior_rings = feature.interiors
        if len(interior_rings) > 0:
            holes = []
            for ring in interior_rings:            
                hole_as_poly = Polygon(ring)
                if hole_as_poly.area <= threshold:
                    holes.append(hole_as_poly)
            filled_holes = unary_union(holes)
        else:
            filled_holes = feature
        # Recombine the filled hole with its parent
        combined = feature.union(filled_holes)
        polys_updated.append(combined)
    
    return gpd.GeoDataFrame(data, geometry=polys_updated, crs=data.crs)


def identify_overlaps(data: gpd.GeoDataFrame, flatten=True) -> gpd.GeoDataFrame:
    """Identify regions of overlap between polygons.
    
    Parameters
    ----------
    data : gpd.GeoDataFrame

    flatten : bool
        Whether or not to flatten the original layer. Regions of overlap
        will be burned into the original geometries, which will be 
        modified to remove any overlap.
    
    Returns
    -------
    gpd.GeoDataFrame
    """
    data = _round_geometries(data)

    groups = (data
        .overlay(data, how='intersection', keep_geom_type=True)
        .explode(index_parts=True)
    )

    # Assume non-overlapping areas will not have the same area
    groups['area'] = groups.area.round(3)
    overlapping_regions = groups.groupby('area').filter(lambda x: len(x) > 1)
    overlapping_regions['overlap'] = 1

    if flatten:
        # Remove duplicate regions
        ovlps = (overlapping_regions
            .dissolve()
            .explode(index_parts=False)
         ) 
        ovlps = _round_geometries(ovlps)

        return update_layer(data, ovlps)
    else:
        return overlapping_regions


def update_layer(original_polys: gpd.GeoDataFrame, 
                 update_polys: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Update a data frame with polygons from another.
    
    The shapes from ``update_polys`` will be "burned" into the original 
    layer(``original_polys``).

    original_polys : gpd.GeoDataFrame
        The original polygon data layer.

    update_polys : gpd.GeoDataFrame
        The data layer with the shapes that will be "burned" into the 
        original layer.

    Returns
    -------
    gpd.GeoDataFrame
    """
    # Remove the regions from the original layer that intersect the 
    # new geometries
    erased = (original_polys
        .overlay(update_polys, how='difference', keep_geom_type=True)
        .explode(index_parts=True)
    )

    # Update ("burn in") the new shapes to the original layer.
    return erased.append(update_polys)


def _fill_boundary(data: gpd.GeoDataFrame):
    """Provide a single, hole-free polygon representing the boundary of
    the original dataset.

    The polygons in the dataset are iteratively buffered until they can
    be coerced to a single Polygon object when unioned. Then, all interior
    boundaries are dissolved, resulting in a single polygon representing
    the boundary of the original dataset.
    
    Parameters
    ----------
    data : gpd.GeoDataFrame

    Returns
    -------
    gpd.GeoDataFrame
    """
    i = 0
    data_buffix = data.buffer(i).unary_union.buffer(-i)
    while data_buffix.geom_type != 'Polygon':
        i += 1
        data_buffix = data.buffer(i).unary_union.buffer(-i)
    print(f'Final pos/neg buffer: {i}.')

    complete_boundary = Polygon(data_buffix.exterior)

    return gpd.GeoDataFrame(geometry=[complete_boundary], crs=data.crs)


def _round_geometries(data_frame: gpd.GeoDataFrame):
    rounded_geoms = []
    for feature in data_frame.geometry:
        rounded_geoms.append(_round_coordinates(feature))
    
    return gpd.GeoDataFrame(data_frame, geometry=rounded_geoms, crs=data_frame.crs)


def _round_coordinates(polygon: Polygon):
    rounded_coords = []
    for pt in polygon.exterior.coords:
        rounded_coords.append((round(pt[0], 3), round(pt[1], 3)))
    
    return Polygon(rounded_coords)
