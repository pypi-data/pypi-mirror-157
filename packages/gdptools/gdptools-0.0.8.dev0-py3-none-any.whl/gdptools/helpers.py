"""Primary functions for poly-to-poly area-weighted mapping."""
import logging
import time
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import geopandas as gpd
import netCDF4
import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr
from pygeos import GEOSException
from shapely.geometry import box
from shapely.geometry import Polygon

from gdptools.ancillary import _check_for_intersection
from gdptools.ancillary import _generate_weights_pershp
from gdptools.ancillary import _get_cells_poly
from gdptools.ancillary import _get_crs
from gdptools.ancillary import _get_data_via_catalog
from gdptools.ancillary import _get_dataframe
from gdptools.ancillary import _get_print_on
from gdptools.ancillary import _get_shp_file
from gdptools.ancillary import _get_wieght_df
from gdptools.stats import get_average_wtime
from gdptools.stats import get_ma_average_wtime

# from numba import jit

logger = logging.getLogger(__name__)


def get_cells_poly_2d(
    xr_a: xr.Dataset, lon_str: str, lat_str: str, in_crs: Any
) -> gpd.GeoDataFrame:
    """Get cell polygons associated with 2d lat/lon coordinates.

    Args:
        xr_a (xr.Dataset): _description_
        lon_str (str): _description_
        lat_str (str): _description_
        in_crs (Any): _description_

    Returns:
        gpd.GeoDataFrame: _description_
    """
    lon = xr_a[lon_str]
    lat = xr_a[lat_str]
    count = 0
    poly = []
    lon_n = [
        lon[i, j]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_jm1 = [
        lon[i, j - 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_ip1_jm1 = [
        lon[i + 1, j - 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_ip1 = [
        lon[i + 1, j]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_ip1_jp1 = [
        lon[i + 1, j + 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_jp1 = [
        lon[i, j + 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_im1_jp1 = [
        lon[i - 1, j + 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_im1 = [
        lon[i - 1, j]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    lon_im1_jm1 = [
        lon[i - 1, j - 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]

    lat_n = [
        lat[i, j]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_jm1 = [
        lat[i, j - 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_ip1_jm1 = [
        lat[i + 1, j - 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_ip1 = [
        lat[i + 1, j]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_ip1_jp1 = [
        lat[i + 1, j + 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_jp1 = [
        lat[i, j + 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_im1_jp1 = [
        lat[i - 1, j + 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_im1 = [
        lat[i - 1, j]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]
    lat_im1_jm1 = [
        lat[i - 1, j - 1]
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lat.shape[1] - 1)
    ]

    # print(len(lon_n), len(lat_n), type(lon_n), np.shape(lon_n))
    numcells = len(lon_n)
    index = np.array(range(numcells))
    i_index = np.empty(numcells)
    j_index = np.empty(numcells)
    count = 0
    for i in range(1, lon.shape[0] - 1):
        for j in range(1, lon.shape[1] - 1):
            i_index[count] = i
            j_index[count] = j
            count += 1

    tpoly_1_lon = [
        [lon_n[i], lon_jm1[i], lon_ip1_jm1[i], lon_ip1[i]] for i in range(numcells)
    ]
    tpoly_1_lat = [
        [lat_n[i], lat_jm1[i], lat_ip1_jm1[i], lat_ip1[i]] for i in range(numcells)
    ]
    # print(len(tpoly_1_lon), tpoly_1_lon[0])
    newp = [Polygon(zip(tpoly_1_lon[i], tpoly_1_lat[i])) for i in range(numcells)]
    p1 = [p.centroid for p in newp]
    # print(type(newp), newp[0], len(p1))

    tpoly_2_lon = [
        [lon_n[i], lon_ip1[i], lon_ip1_jp1[i], lon_jp1[i]] for i in range(numcells)
    ]
    tpoly_2_lat = [
        [lat_n[i], lat_ip1[i], lat_ip1_jp1[i], lat_jp1[i]] for i in range(numcells)
    ]
    print(len(tpoly_2_lon), tpoly_2_lon[0])
    newp = [Polygon(zip(tpoly_2_lon[i], tpoly_2_lat[i])) for i in range(numcells)]
    p2 = [p.centroid for p in newp]

    tpoly_3_lon = [
        [lon_n[i], lon_jp1[i], lon_im1_jp1[i], lon_im1[i]] for i in range(numcells)
    ]
    tpoly_3_lat = [
        [lat_n[i], lat_jp1[i], lat_im1_jp1[i], lat_im1[i]] for i in range(numcells)
    ]
    # print(len(tpoly_3_lon), tpoly_3_lon[0])
    newp = [Polygon(zip(tpoly_3_lon[i], tpoly_3_lat[i])) for i in range(numcells)]
    p3 = [p.centroid for p in newp]

    tpoly_4_lon = [
        [lon_n[i], lon_im1[i], lon_im1_jm1[i], lon_jm1[i]] for i in range(numcells)
    ]
    tpoly_4_lat = [
        [lat_n[i], lat_im1[i], lat_im1_jm1[i], lat_jm1[i]] for i in range(numcells)
    ]
    # print(len(tpoly_3_lon), tpoly_3_lon[0])
    newp = [Polygon(zip(tpoly_4_lon[i], tpoly_4_lat[i])) for i in range(numcells)]
    p4 = [p.centroid for p in newp]

    lon_point_list = [[p1[i].x, p2[i].x, p3[i].x, p4[i].x] for i in range(numcells)]
    lat_point_list = [[p1[i].y, p2[i].y, p3[i].y, p4[i].y] for i in range(numcells)]

    poly = [Polygon(zip(lon_point_list[i], lat_point_list[i])) for i in range(numcells)]

    df = pd.DataFrame({"i_index": i_index, "j_index": j_index})
    gmcells = gpd.GeoDataFrame(df, index=index, geometry=poly, crs=in_crs)
    # tpoly_1 = [Polygon(x) for x in newp]
    # p1 = tpoly_1.centroid
    return gmcells


def generate_weights(
    poly: gpd.GeoDataFrame,
    poly_idx: str,
    grid_cells: gpd.GeoDataFrame,
    grid_cells_crs: str,
    wght_gen_crs: str,
    filename: Optional[str] = None,
) -> pd.DataFrame:
    """Generate weights for aggragations of poly-to-poly mapping.

    Args:
        poly (gpd.GeoDataFrame): _description_
        poly_idx (str): _description_
        grid_cells (gpd.GeoDataFrame): _description_
        grid_cells_crs (str): _description_
        wght_gen_crs (str): _description_
        filename (Optional[str], optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        pd.DataFrame: _description_
    """
    # check if poly_idx in in poly
    if poly_idx not in poly.columns:
        error_string = (
            f"Error: poly_idx ({poly_idx}) is not found in the poly ({poly.columns})"
        )
        raise ValueError(error_string)

    if not poly.crs:
        error_string = f"polygons don't contain a valid crs: {poly.crs}"
        raise ValueError(error_string)

    grid_in_crs = _get_crs(grid_cells_crs)
    grid_out_crs = _get_crs(wght_gen_crs)

    start = time.perf_counter()
    grid_cells.set_crs(grid_in_crs, inplace=True)
    grid_cells.to_crs(grid_out_crs, inplace=True)

    poly.to_crs(grid_out_crs, inplace=True)
    end = time.perf_counter()
    print(
        f"Reprojecting to epsg:{wght_gen_crs} finished in {round(end-start, 2)}"
        " second(s)"
    )

    start = time.perf_counter()
    spatial_index = grid_cells.sindex
    # print(type(spatial_index))
    end = time.perf_counter()
    print(f"Spatial index generations finished in {round(end-start, 2)} second(s)")
    start = time.perf_counter()
    tcount = 0

    numrows = len(poly.index)
    print_on = _get_print_on(numrows)

    # in order, i_index, j_index, poly_index, weight values
    i_index = []
    j_index = []
    p_index = []
    wghts = []

    for index, row in poly.iterrows():
        count = 0
        hru_area = poly.loc[poly[poly_idx] == row[poly_idx]].geometry.area.sum()
        try:
            possible_matches_index = list(
                spatial_index.intersection(row["geometry"].bounds)
            )
        except AttributeError:
            print(f"User feature Attribute error index: {index} has an error")

        if not (len(possible_matches_index) == 0):
            possible_matches = grid_cells.iloc[possible_matches_index]
            try:
                precise_matches = possible_matches[
                    possible_matches.intersects(row["geometry"])
                ]
            except GEOSException:
                print(f"User feature GEOSException error: index={index}, row={row}")
            except TypeError:
                print(f"User feature Type error: index={index}, row={row}")
            if not (len(precise_matches) == 0):
                res_intersection = gpd.overlay(
                    poly.loc[[index]], precise_matches, how="intersection"
                )
                for nindex, row in res_intersection.iterrows():

                    tmpfloat = float(res_intersection.area.iloc[nindex] / hru_area)
                    i_index.append(int(row["i_index"]))
                    j_index.append(int(row["j_index"]))
                    p_index.append(str(row[poly_idx]))
                    wghts.append(tmpfloat)
                    count += 1
                tcount += 1
                if tcount % print_on == 0:
                    print(tcount, index, flush=True)

        else:
            print("no intersection: ", index, str(row[poly_idx]), flush=True)

    wght_df = pd.DataFrame(
        {
            poly_idx: p_index,
            "i": i_index,
            "j": j_index,
            "wght": wghts,
        }
    )
    wght_df = wght_df.astype({"i": int, "j": int, "wght": float, poly_idx: str})
    if filename:
        wght_df.to_csv(filename)
    end = time.perf_counter()
    print(f"Weight generations finished in {round(end-start, 2)} second(s)")
    return wght_df


def run_weights(
    var: str,
    time: str,
    ds: xr.Dataset,
    wght_file: Union[str, pd.DataFrame],
    shp: gpd.GeoDataFrame,
    geom_id: str,
) -> Tuple[gpd.GeoDataFrame, npt.NDArray[Any]]:
    """Run aggregation mapping ds to shp.

    Args:
        var (str): _description_
        time (str): _description_
        ds (xr.Dataset): _description_
        wght_file (Union[str, pd.DataFrame]): _description_
        shp (gpd.GeoDataFrame): _description_
        geom_id (str): _description_

    Returns:
        Tuple[gpd.GeoDataFrame, npt.NDArray[Any]]: _description_
    """
    wghts = _get_wieght_df(wght_file, geom_id)

    gdf = shp
    # gdf.reset_index(drop=True, inplace=True)
    # gdf1 = gdf.sort_values(geom_id).dissolve(by=geom_id)
    gdf1 = gdf.dissolve(by=geom_id)

    geo_index = np.asarray(gdf1.index, dtype=str)
    n_geo = len(geo_index)

    print_on = _get_print_on(n_geo)
    unique_geom_ids = wghts.groupby(geom_id)
    ds_vars = [i for i in ds.data_vars]
    # if var not in ds_vars:
    #     raise KeyError(f"var: {var} not in ds vars: {ds_vars}")
    #     return None, None

    nts = len(ds.coords[time].values)
    try:
        native_dtype = ds[var].values.dtype
    except KeyError:
        print(f"var: {var} not in ds vars: {ds_vars}")

    val_interp = np.empty((n_geo, nts), dtype=native_dtype)
    var_vals = ds[var].values

    # for t in np.arange(nts):
    #     # val_flat_interp = (
    #     #     ds[var].values[t, 1 : grd_shp[1] - 1, 1 : grd_shp[2] - 1].flatten()
    #     # )
    print(f"processing time for var: {var}")
    for i in np.arange(len(geo_index)):
        weight_id_rows = unique_geom_ids.get_group(geo_index[i])
        tw = weight_id_rows.wght.values
        i_ind = np.array(weight_id_rows.i.values)
        j_ind = np.array(weight_id_rows.j.values)

        vals = var_vals[:, i_ind, j_ind]

        # tgid = weight_id_rows.grid_ids.values
        # tmp = getaverage(val_flat_interp[tgid], tw)
        tmp = get_average_wtime(vals, tw)
        try:
            if np.isnan(tmp).any():
                val_interp[i, :] = get_ma_average_wtime(vals, tw)
            else:
                val_interp[i, :] = tmp
        except KeyError:
            val_interp[i, :] = netCDF4.default_fillvals["f8"]

        if i % print_on == 0:
            print(f"    Processing {var} for feature {geo_index[i]}", flush=True)

    # print(val_interp)
    return gdf1, val_interp


def build_subset(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    tname: str,
    toptobottom: bool,
    date_min: str,
    date_max: Optional[str] = None,
) -> Dict[str, object]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Args:
        bounds (np.ndarray): _description_
        xname (str): _description_
        yname (str): _description_
        tname (str): _description_
        toptobottom (bool): _description_
        date_min (str): _description_
        date_max (Optional[str], optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]
    ss_dict = {}
    if not toptobottom:
        if date_max is None:
            ss_dict = {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: date_min,
            }
        else:
            ss_dict = {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: slice(date_min, date_max),
            }
    else:
        if date_max is None:
            ss_dict = {
                xname: slice(minx, maxx),
                yname: slice(miny, maxy),
                tname: date_min,
            }
        else:
            ss_dict = {
                xname: slice(minx, maxx),
                yname: slice(miny, maxy),
                tname: slice(date_min, date_max),
            }
    return ss_dict


def calc_weights_catalog(
    params_json: Union[str, pd.DataFrame],
    grid_json: Union[str, pd.DataFrame],
    shp_file: Union[str, gpd.GeoDataFrame],
    shp_poly_idx: str,
    wght_gen_proj: Any,
    wght_gen_file: Optional[str] = None,
) -> pd.DataFrame:
    """Calculate area-intersected weights of grid to feature.

    Args:
        params_json (Union[str, pd.DataFrame]): _description_
        grid_json (Union[str, pd.DataFrame]): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        shp_poly_idx (str): _description_
        wght_gen_proj (Any): _description_
        wght_gen_file (Optional[str], optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        pd.DataFrame: _description_
    """
    params_json = _get_dataframe(params_json)
    grid_json = _get_dataframe(grid_json)
    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf, gdf_bounds = _get_shp_file(shp_file=shp_file, grid_json=grid_json)

    #run check on intersection of shape features and gridded data
    is_intersect, is_degrees, is_0_360 = _check_for_intersection(
        params_json=params_json, grid_json=grid_json, gdf=gdf
    )
    # ds_URL = params_json.URL.values[0]
    ds_proj = grid_json.proj.values[0]
    # only need one time step for generating weights so choose the first time from the param_cat
    date = params_json.duration.values[0].split("/")[0]



    date = params_json.duration.values[0].split("/")[0]
    # get sub-setted xarray dataset

    if (not is_intersect) & is_degrees & (not is_0_360):
        rotate_ds = True
    else:
        rotate_ds = False
    ds_ss = _get_data_via_catalog(
        params_json=params_json,
        grid_json=grid_json,
        bounds=gdf_bounds,
        begin_date=date,
        rotate_lon=rotate_ds,
    )

    # get grid polygons to calculate intersection with polygon of interest - shp_file
    xname = grid_json.X_name.values[0]
    yname = grid_json.Y_name.values[0]
    var = params_json.variable.values[0]
    gdf_grid = _get_cells_poly(ds_ss, x=xname, y=yname, var=var, crs_in=ds_proj)

    # calculate the intersection weights and generate weight_file
    # assumption is that the first column in the shp_file is the id to use for
    # calculating weights
    if shp_poly_idx not in gdf.columns[:]:
        raise ValueError(
            f"shp_poly_idx: {shp_poly_idx} not in gdf columns: {gdf.columns}"
        )
    else:
        apoly_idx = shp_poly_idx

    wght_gen = generate_weights(
        poly=gdf,
        poly_idx=apoly_idx,
        grid_cells=gdf_grid,
        grid_cells_crs=grid_json.proj.values[0],
        filename=wght_gen_file,
        wght_gen_crs=wght_gen_proj,
    )

    return wght_gen


def calc_weights_catalog_pershp(
    params_json: Union[str, pd.DataFrame],
    grid_json: Union[str, pd.DataFrame],
    shp_file: Union[str, gpd.GeoDataFrame],
    shp_poly_idx: str,
    wght_gen_proj: Any,
) -> pd.DataFrame:
    """Calculate area-intersected weights of grid to feature.

    Args:
        params_json (Union[str, pd.DataFrame]): _description_
        grid_json (Union[str, pd.DataFrame]): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        shp_poly_idx (str): _description_
        wght_gen_proj (Any): _description_

    Raises:
        ValueError: _description_

    Returns:
        pd.DataFrame: _description_
    """
    params_json = _get_dataframe(params_json)
    grid_json = _get_dataframe(grid_json)

    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf, gdf_bounds = _get_shp_file(shp_file=shp_file, grid_json=grid_json)

    # run check on intersection of shape features and gridded data
    is_intersect, is_degrees, is_0_360 = _check_for_intersection(
        params_json=params_json, grid_json=grid_json, gdf=shp_file
    )
    # ds_URL = params_json.URL.values[0]
    ds_proj = grid_json.proj.values[0]
    # only need one time step for generating weights so choose the first time from the param_cat
    date = params_json.duration.values[0].split("/")[0]

    # get sub-setted xarray dataset
    if (not is_intersect) & is_degrees & (not is_0_360):
        rotate_ds = True
    else:
        rotate_ds = False
    ds_ss = _get_data_via_catalog(
        params_json=params_json,
        grid_json=grid_json,
        bounds=gdf_bounds,
        begin_date=date,
        rotate_lon=rotate_ds,
    )

    # get grid polygons to calculate intersection with polygon of interest - shp_file
    xname = grid_json.X_name.values[0]
    yname = grid_json.Y_name.values[0]
    var = params_json.variable.values[0]
    gdf_grid = _get_cells_poly(ds_ss, x=xname, y=yname, var=var, crs_in=ds_proj)

    # calculate the intersection weights and generate weight_file
    # assumption is that the first column in the shp_file is the id to use for
    # calculating weights
    if shp_poly_idx not in gdf.columns[:]:
        raise ValueError(
            f"shp_poly_idx: {shp_poly_idx} not in gdf columns: {gdf.columns}"
        )
    else:
        apoly_idx = shp_poly_idx

    wght_gen = _generate_weights_pershp(
        poly=shp_file,
        poly_idx=apoly_idx,
        grid_cells=gdf_grid,
        grid_cells_crs=grid_json.proj.values[0],
        wght_gen_crs=wght_gen_proj,
    )

    return wght_gen


def run_weights_catalog_pershp(
    params_json: pd.DataFrame,
    grid_json: pd.DataFrame,
    wght_file: pd.DataFrame,
    shp: gpd.GeoDataFrame,
    begin_date: str,
    end_date: str,
) -> Tuple[gpd.GeoDataFrame, npt.NDArray[np.double]]:
    """Run area-weighted aggragation of grid to feature.

    Args:
        params_json (pd.DataFrame): _description_
        grid_json (pd.DataFrame): _description_
        wght_file (pd.DataFrame): _description_
        shp (gpd.GeoDataFrame): _description_
        begin_date (str): _description_
        end_date (str): _description_

    Returns:
        Union[gpd.GeoDataFrame, np.ndarray]: _description_
    """
    poly_idx = shp.columns[0]
    wghts = _get_wieght_df(wght_file, poly_idx)

    # read shapefile, calculate total_bounds, and project to grid's projection
    shp.to_crs(grid_json.proj.values[0], inplace=True)
    bbox = box(*shp.total_bounds)
    b_buf = max(grid_json.resX.values[0], grid_json.resY.values[0])
    gdf_bounds = bbox.buffer(2 * b_buf).bounds
    # gdf_bounds = shp.total_bounds

    # get sub-setted xarray dataset
    ds = _get_data_via_catalog(
        params_json=params_json,
        grid_json=grid_json,
        bounds=gdf_bounds,
        begin_date=begin_date,
        end_date=end_date,
    )

    # shp.reset_index(drop=True, inplace=True)
    gdf1 = shp.dissolve(by=poly_idx)

    geo_index = np.asarray(gdf1.index, dtype=type(gdf1.index.values[0]))
    n_geo = len(geo_index)

    print_on = _get_print_on(n_geo)
    unique_geom_ids = wghts.groupby(poly_idx)

    var = str(params_json.varname.values[0])
    time = str(params_json.T_name.values[0])
    ds_vars = [i for i in ds.data_vars]
    # if var not in ds_vars:
    #     raise KeyError(f"var: {var} not in ds vars: {ds_vars}")
    #     return None, None

    nts = len(ds.coords[time].values)
    try:
        native_dtype = ds[var].values.dtype
    except KeyError:
        print(f"var: {var} not in ds vars: {ds_vars}")
    val_interp = np.empty(nts, dtype=native_dtype)
    # dvar = np.array([var for _ in range(nts)], dtype=str)
    # dates = ds.coords[time].values
    var_vals = ds[var].values
    i = 0
    # for t in np.arange(nts):
    #     # val_flat_interp = (
    #     #     ds[var].values[t, 1 : grd_shp[1] - 1, 1 : grd_shp[2] - 1].flatten()
    #     # )
    # for i in np.arange(len(geo_index)):

    weight_id_rows = unique_geom_ids.get_group(str(geo_index[i]))
    tw = weight_id_rows.wght.values
    i_ind = np.array(weight_id_rows.i.values)
    j_ind = np.array(weight_id_rows.j.values)

    vals = var_vals[:, i_ind, j_ind]

    # tgid = weight_id_rows.grid_ids.values
    # tmp = getaverage(val_flat_interp[tgid], tw)
    tmp = get_average_wtime(vals, tw)
    try:
        if np.isnan(tmp).any():
            val_interp[:] = get_ma_average_wtime(vals, tw)
        else:
            val_interp[:] = tmp
    except KeyError:
        val_interp[:] = netCDF4.default_fillvals["f8"]

    if i % print_on == 0:
        print(f"    Processing {var} for feature {geo_index[i]}", flush=True)

    # print(val_interp)
    # pd_data = {"variable": dvar}
    # # ndf = pd.DataFrame(pd_data)
    # ndf = pd.DataFrame(
    #     pd_data, index=pd.DatetimeIndex(dates, name="date"), columns=[geo_index[:]]
    # )
    # ndf[geo_index[i]] = val_interp
    return gdf1, val_interp


def run_weights_catalog(
    params_json: Union[str, pd.DataFrame],
    grid_json: Union[str, pd.DataFrame],
    wght_file: Union[str, pd.DataFrame],
    shp_file: Union[str, gpd.GeoDataFrame],
    shp_poly_idx: str,
    begin_date: str,
    end_date: str,
) -> Tuple[gpd.GeoDataFrame, npt.NDArray[np.double]]:
    """Run area-weighted aggragation of grid to feature.

    Args:
        params_json (Union[str, pd.DataFrame]): _description_
        grid_json (Union[str, pd.DataFrame]): _description_
        wght_file (Union[str, pd.DataFrame]): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        shp_poly_idx (str): _description_
        begin_date (str): _description_
        end_date (str): _description_

    Raises:
        ValueError: _description_

    Returns:
        Union[gpd.GeoDataFrame, np.ndarray]: _description_
    """
    params_json = _get_dataframe(params_json)
    grid_json = _get_dataframe(grid_json)

    # read shapefile, calculate total_bounds, and project to grid's projection
    shp, gdf_bounds = _get_shp_file(shp_file=shp_file, grid_json=grid_json)

    # run check on intersection of shape features and gridded data
    is_intersect, is_degrees, is_0_360 = _check_for_intersection(
        params_json=params_json, grid_json=grid_json, gdf=shp_file
    )
    # read shapefile, calculate total_bounds, and project to grid's projection
    shp, gdf_bounds = _get_shp_file(shp_file=shp_file, grid_json=grid_json)
    poly_idx = shp_poly_idx
    if poly_idx not in shp.columns[:]:
        raise ValueError(
            (f"shp_poly_idx: {poly_idx}" " not in gdf columns: {shp.columns}")
        )

    wghts = _get_wieght_df(wght_file, poly_idx)

    # get sub-setted xarray dataset
    if (not is_intersect) & is_degrees & (not is_0_360):
        rotate_ds = True
    else:
        rotate_ds = False
    da = _get_data_via_catalog(
        params_json=params_json,
        grid_json=grid_json,
        bounds=gdf_bounds,
        begin_date=begin_date,
        end_date=end_date,
        rotate_lon=rotate_ds,
    )
    #     da.load()
    #     dslist.append(da)
    # da = xr.concat(dslist, axis=params_json.T_name.values[0])

    shp.reset_index(drop=True, inplace=True)
    gdf = shp.sort_values(poly_idx).dissolve(by=poly_idx)
    # gdf = shp.dissolve(by=poly_idx)

    geo_index = np.asarray(gdf.index, dtype=type(gdf.index.values[0]))
    n_geo = len(geo_index)

    print_on = _get_print_on(n_geo)
    unique_geom_ids = wghts.groupby(poly_idx)

    var = str(params_json.varname.values[0])
    time = str(params_json.T_name.values[0])
    # ds_vars = [i for i in da.data_vars]
    # if var not in ds_vars:
    #     raise KeyError(f"var: {var} not in da vars: {ds_vars}")
    #     return None, None

    nts = len(da.coords[time].values)
    # tv = da.coords[time].values
    native_dtype = da.dtype
    val_interp = np.empty((n_geo, nts), dtype=native_dtype)

    try:
        print(f"loading {var} values", flush=True)
        da.load()
        # var_vals = da.values()
        print(f"finished loading {var} values", flush=True)
    except Exception:
        print("error loading data")

    for i in np.arange(len(geo_index)):
        weight_id_rows = unique_geom_ids.get_group(str(geo_index[i]))
        tw = weight_id_rows.wght.values
        i_ind = np.array(weight_id_rows.i.values)
        j_ind = np.array(weight_id_rows.j.values)

        vals = da.values[:, i_ind, j_ind]
        tmp = get_average_wtime(vals, tw)

        try:
            if np.isnan(tmp[:]).any():
                val_interp[i, :] = netCDF4.default_fillvals["f8"]
            else:
                val_interp[i, :] = tmp
        except KeyError:
            val_interp[i, :] = netCDF4.default_fillvals["f8"]

        if i % print_on == 0:
            print(f"    Processing {var} for feature {geo_index[i]}", flush=True)

    return gdf, val_interp


def get_data_subset_catalog(
    params_json: Union[str, pd.DataFrame],
    grid_json: Union[str, pd.DataFrame],
    shp_file: Union[str, gpd.GeoDataFrame],
    begin_date: str,
    end_date: str,
) -> xr.DataArray:
    """Get xarray subset data.

    Args:
        params_json (Union[str, pd.DataFrame]): _description_
        grid_json (Union[str, pd.DataFrame]): _description_
        shp_file (Union[str, gpd.GeoDataFrame]): _description_
        begin_date (str): _description_
        end_date (str): _description_

    Returns:
        xr.Dataset: _description_
    """
    params_json = _get_dataframe(params_json)
    grid_json = _get_dataframe(grid_json)
    # read shapefile, calculate total_bounds, and project to grid's projection
    shp, gdf_bounds = _get_shp_file(shp_file=shp_file, grid_json=grid_json)

    # get sub-setted xarray dataset
    ds = _get_data_via_catalog(
        params_json=params_json,
        grid_json=grid_json,
        bounds=gdf_bounds,
        begin_date=begin_date,
        end_date=end_date,
    )

    return ds
