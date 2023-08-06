"""kernal functions for poly-to-poly area-weighted mapping."""
import logging
from typing import Any
from typing import Union

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pandas as pd
from shapely.geometry import box

from .ancillary import _generate_weights_pershp
from .ancillary import _get_cells_poly
from .ancillary import _get_data_via_catalog
from .ancillary import _get_dataframe
from .helpers import run_weights_catalog_pershp

logger = logging.getLogger(__name__)


def intersect_by_weighted_area(
    params_json: Union[str, pd.DataFrame],
    grid_json: Union[str, pd.DataFrame],
    gdf: gpd.GeoDataFrame,
    begin_date: str,
    end_date: str,
    wght_gen_proj: Any,
) -> Union[gpd.GeoDataFrame, npt.NDArray[np.double]]:
    """Calculate weighted-area-intersection between grid and shape.

    Args:
        params_json (Union[str, pd.DataFrame]): _description_
        grid_json (Union[str, pd.DataFrame]): _description_
        gdf (gpd.GeoDataFrame): _description_
        begin_date (str): _description_
        end_date (str): _description_
        wght_gen_proj (Any): _description_

    Returns:
        Union[gpd.GeoDataFrame, np.ndarray]: _description_
    """
    pjson = _get_dataframe(params_json)
    gjson = _get_dataframe(grid_json)
    # ds_URL = params_json.URL.values[0]
    ds_proj = gjson.proj.values[0]
    # only need one time step for generating weights so choose the first time from the param_cat
    date = pjson.duration.values[0].split("/")[0]

    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf.to_crs(gjson.proj.values[0], inplace=True)
    bbox = box(*gdf.total_bounds)
    b_buf = max(gjson.resX.values[0], gjson.resY.values[0])
    geo_s_bounds = bbox.buffer(2 * b_buf).bounds
    # geo_s_bounds = gdf.total_bounds

    date = pjson.duration.values[0].split("/")[0]
    # get sub-setted xarray dataset
    ds_ss = _get_data_via_catalog(
        params_json=pjson,
        grid_json=gjson,
        bounds=geo_s_bounds,
        begin_date=date,
    )
    # get grid polygons to calculate intersection with polygon of interest - shp_file
    xname = gjson.X_name.values[0]
    yname = gjson.Y_name.values[0]
    var = pjson.variable.values[0]
    gdf_grid = _get_cells_poly(ds_ss, x=xname, y=yname, var=var, crs_in=ds_proj)
    # gdf_grid = gpd.GeoDataFrame.from_features(gridpoly, crs=ds_proj)

    # calculate the intersection weights and generate weight_file
    # assumption is that the first column in the shp_file is the id to use for
    # calculating weights
    apoly_idx = gdf.columns[0]
    wght_gen = _generate_weights_pershp(
        poly=gdf,
        poly_idx=apoly_idx,
        grid_cells=gdf_grid,
        grid_cells_crs=gjson.proj.values[0],
        wght_gen_crs=wght_gen_proj,
    )

    newgdf, vals = run_weights_catalog_pershp(
        params_json=pjson,
        grid_json=gjson,
        wght_file=wght_gen,
        shp=gdf,
        begin_date=begin_date,
        end_date=end_date,
    )
    return newgdf, vals
