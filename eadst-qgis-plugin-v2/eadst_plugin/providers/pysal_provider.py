# -*- coding: utf-8 -*-
"""A provider/wrapper for PySAL spatial analysis functions."""

import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran_Local

def run_lisa_analysis(geopackage_path, layer_name, attribute_column):
    """
    Runs a LISA analysis on a given layer and attribute.

    :param geopackage_path: Path to the GeoPackage file.
    :param layer_name: Name of the layer within the GeoPackage.
    :param attribute_column: The column to analyze.
    
    :returns: GeoDataFrame with LISA results appended.
    """
    try:
        gdf = gpd.read_file(geopackage_path, layer=layer_name)
        
        # Create spatial weights
        weights = Queen.from_dataframe(gdf)
        weights.transform = 'r'

        # Calculate Local Moran's I
        lisa = Moran_Local(gdf[attribute_column], weights)
        
        # Append results to the GeoDataFrame
        gdf['lisa_q'] = lisa.q
        gdf['lisa_p_sim'] = lisa.p_sim
        
        return gdf

    except Exception as e:
        print(f"An error occurred in PySAL provider: {e}")
        return None