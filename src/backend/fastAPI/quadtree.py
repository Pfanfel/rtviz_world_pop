import xarray as xr
import numpy as np
import pandas as pd
from pyquadkey2 import quadkey
import pprint
import json


def build_quadtree():

    # dataset = xr.open_dataset(
    #     "../../data/gpw_v4_basic_demographic_characteristics_rev11_mt_2010_dens_2pt5_min.nc"
    # )
    # print(dataset)
    # lat_slice = slice(55, 45)
    # lon_slice = slice(6, 15)
    # print(dataset.data_vars)
    # data_slice = dataset.sel(latitude=lat_slice, longitude=lon_slice)
    # print(dataset.attrs)
    # # data_slice = dataset[
    # #     "Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes"
    # # ]
    # # data_slice = data_slice.compute()
    # # print(data_slice)
    # data_slice_male_pop_density_age_0_4 = data_slice[2]
    # data_slice_male_pop_density_age_0_4 = data_slice.compute()
    # print(data_slice_male_pop_density_age_0_4)
    # [['raster', 'Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes']]

    file_path_male = "../../data/gpw_v4_basic_demographic_characteristics_rev11_mt_2010_dens_2pt5_min.nc"
    lat_slice = slice(55, 45)
    lon_slice = slice(6, 15)
    data_slice_male = load_dataset(file_path_male, lat_slice, lon_slice)

    datapoints_male = extract_data_points(data_slice_male)

    zoom_level_2 = create_quadtree(datapoints_male, 2)
    zoom_level_13 = create_quadtree(datapoints_male, 13)

    # Display quadtree
    # for key, value in zoom_level_1.items():
    #     print(f"Quadkey_1: {key}, Data: {value}")

    # for key, value in zoom_level_2.items():
    #     print(f"Quadkey_2: {key}, Data: {value}")

    # zoom_level_2_json = json.dumps(zoom_level_2, indent=4)
    # zoom_level_13_json = json.dumps(zoom_level_13, indent=4)

    return zoom_level_2, zoom_level_13


def create_quadtree(data_points, zoom_level):

    # Initialize quadtree structure (dictionary)
    quadtree = {}

    # Process each data point
    for point in data_points:
        # Convert latitude and longitude to a quadkey
        tile = quadkey.from_geo(point[0], zoom_level)
        quadkey_str = tile.key

        # Group data by quadkey
        if quadkey_str not in quadtree:
            quadtree[quadkey_str] = []
        quadtree[quadkey_str].append(point)

    return quadtree


def load_dataset(file_path, lat_slice, lon_slice):
    dataset = xr.open_dataset(file_path)
    data_slice = dataset.sel(latitude=lat_slice, longitude=lon_slice)
    data_slice = data_slice[
        "Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes"
    ]
    return data_slice.compute()


def extract_data_points(data_slice_male):
    data_points = []
    longs = data_slice_male.longitude.values
    lats = data_slice_male.latitude.values

    for x in range(0, 10 * 24 - 1):
        for y in range(0, 9 * 24 - 1):
            data_point2 = ((longs[y], lats[x]), [])
            for r in range(0, 29):
                data_point2[1].append(data_slice_male.values[r][x][y])
            data_points.append(data_point2)

    return data_points


if __name__ == "__main__":
    zoom_level_2, zoom_level_13 = build_quadtree()
    # pprint.pprint(zoom_level_2)
    # pprint.pprint(zoom_level_13)
