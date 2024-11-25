import xarray as xr
import numpy as np
import pandas as pd
from pyquadkey2 import quadkey
import pprint
import json

# def check_ancestor(df, ancestor_quadkey_str):
#     # Create a QuadKey object for the ancestor to check against
#     ancestor_quadkey = quadkey.QuadKey(ancestor_quadkey_str)

#     # Define a lambda function to check if the current quadkey in the DataFrame is an ancestor
#     df["is_ancestor"] = df["quadkey"].apply(
#         lambda x: ancestor_quadkey.is_ancestor(quadkey.QuadKey(str(x)))
#     )
#     return df


# def check_descendent(df, ancestor_quadkey_str):
#     # Create a QuadKey object for the ancestor to check against
#     ancestor_quadkey = quadkey.QuadKey(ancestor_quadkey_str)

#     # Define a lambda function to check if the current quadkey in the DataFrame is an ancestor
#     df["is_ancestor"] = df["quadkey"].apply(
#         lambda x: ancestor_quadkey.is_descendent(quadkey.QuadKey(str(x)))
#     )
#     return df


def filter_by_ancestor(df, ancestor_quadkey_str):
    # Create a QuadKey object for the ancestor to check against
    ancestor_quadkey = quadkey.QuadKey(ancestor_quadkey_str)

    # Filter the DataFrame by keeping only rows where the quadkey is an ancestor
    filtered_df = df[
        df["quadkey"].apply(
            lambda x: ancestor_quadkey.is_ancestor(quadkey.QuadKey(str(x)))
        )
    ]

    return filtered_df


def filter_by_descendent(df, ancestor_quadkey_str):
    # Create a QuadKey object for the ancestor to check against
    ancestor_quadkey = quadkey.QuadKey(ancestor_quadkey_str)

    # Filter the DataFrame by keeping only rows where the quadkey is a descendant
    filtered_df = df[
        df["quadkey"].apply(
            lambda x: ancestor_quadkey.is_descendent(quadkey.QuadKey(str(x)))
        )
    ]

    return filtered_df


def df_to_json(df):
    json_result = df.to_json(orient="records")
    # formatted_json = json.dumps(
    #     json_result, indent=2
    # )  # is not necessary, but makes the output more readable
    return json_result


def load_male_dataset():

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
    file_path_male_raster_lookup = "../../data/gpw_v4_basic_demographic_characteristics_rev11_mt_2010_dens_2pt5_min_lookup.csv"
    df_file_path_male_raster_lookup = read_csv_file(file_path_male_raster_lookup)
    raster_column_values = get_column_values(
        df_file_path_male_raster_lookup, "raster_name"
    )

    raster_column_values_lowercased = process_raster_names(raster_column_values)
    print(raster_column_values_lowercased)

    lat_slice = slice(85, -85)  # Dosen't work with value over 85 or under -85
    lon_slice = slice(6, 7)
    data_slice_male = load_dataset(file_path_male, lat_slice, lon_slice)

    data_slice_male_long_lat = extract_data_points_vectorized_long_lat(
        data_slice_male, raster_column_values_lowercased
    )
    # data_slice_male_quadkey = extract_data_points_vectorized_quadkey(data_slice_male)

    print(data_slice_male_long_lat.head())
    print(data_slice_male_long_lat.tail())

    # print(data_slice_male_quadkey.head())
    # print(data_slice_male_quadkey.tail())
    # print(data_slice_male_quadkey.info())

    # updated_df = filter_by_descendent(data_slice_male_quadkey, "12020320231")
    # print("---After query---")
    # print(updated_df.head())
    # print(updated_df.tail())
    # print(reshaped_df.columns)
    # print(reshaped_df.shape)
    # print(updated_df.info())

    # data_slice_male_np = data_slice_male.as_numpy()
    ##print(np.info(data_slice_male_np))

    # datapoints_male = extract_data_points(data_slice_male)

    # zoom_level_2 = create_quadtree(datapoints_male, 2)
    # zoom_level_13 = create_quadtree(datapoints_male, 13)

    # Display quadtree
    # for key, value in zoom_level_1.items():
    #     print(f"Quadkey_1: {key}, Data: {value}")

    # for key, value in zoom_level_2.items():
    #     print(f"Quadkey_2: {key}, Data: {value}")

    # zoom_level_2_json = json.dumps(zoom_level_2, indent=4)
    # zoom_level_13_json = json.dumps(zoom_level_13, indent=4)

    return data_slice_male_quadkey


def process_raster_names(raster_names):
    processed_names = []
    for name in raster_names:
        if ":" in name:
            extracted_name = name.split(":", 1)[1].strip().lower().replace(" ", "_")
            processed_names.append(extracted_name)
    return processed_names


def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    print(df.head())
    print(df.tail())
    print(df.columns)
    print(df.shape)
    print(df.info())
    return df


def get_column_values(df, column_name):
    if column_name in df.columns:
        return df[column_name].tolist()
    else:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame")


def extract_data_points_vectorized_long_lat(ds, raster_column_values_lowercased):
    # Convert the dataset to a pandas DataFrame
    df = (
        ds.to_dataframe().reset_index()
    )  # .reset_index() is used to convert the index to columns

    # print("---Before reshaping---")
    # print(df.head())
    # print(df.tail())
    # print(df.columns)
    # print(df.shape)
    # print(df.info())

    # Assuming 'df' is your original DataFrame with the columns shown
    df.columns = [
        "raster",
        "latitude",
        "longitude",
        "Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes",
    ]

    # Use pivot for vectorized reshaping
    reshaped_df = df.pivot(
        index=["latitude", "longitude"],
        columns="raster",
        values="Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes",
    )

    # Reset the index to turn 'latitude' and 'longitude' back into columns
    reshaped_df.reset_index(inplace=True)

    # Rename the raster columns to have a prefix
    reshaped_df.columns = ["latitude", "longitude"] + [
        raster_column_values_lowercased[int(col) - 1] if not pd.isnull(col) else col
        for col in reshaped_df.columns[2:]
    ]

    # print("---After reshaping---")
    # print(reshaped_df.head())
    # print(reshaped_df.tail())
    # print(reshaped_df.columns)
    # print(reshaped_df.shape)
    # print(reshaped_df.info())

    return reshaped_df


def extract_data_points_vectorized_quadkey(ds):
    # Convert the dataset to a pandas DataFrame
    df = (
        ds.to_dataframe().reset_index()
    )  # .reset_index() is used to convert the index to columns

    # print("---Before reshaping---")
    # print(df.head())
    # print(df.tail())
    # print(df.columns)
    # print(df.shape)
    # print(df.info())

    df.columns = [
        "raster",
        "latitude",
        "longitude",
        "Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes",
    ]

    # Convert latitude and longitude to a quadkey with a specified level (e.g., 12)
    level = 14  #  60/2,5 = 24 datapoints per degree 8640 points around the world, 2^14 = 16384
    # When using level 13: ValueError: Index contains duplicate entries, cannot reshape

    df["quadkey"] = df.apply(
        lambda row: int(
            quadkey.from_geo((row["latitude"], row["longitude"]), level).key
        ),
        axis=1,
    )

    # Use the new 'quadkey' column as the index for pivoting
    reshaped_df = df.pivot(
        index="quadkey",
        columns="raster",
        values="Basic Demographic Characteristics, v4.10 (2010): Male, Density, 2.5 arc-minutes",
    )

    # Reset the index to turn 'quadkey' back into a column if needed
    reshaped_df.reset_index(inplace=True)

    # Rename the raster columns to have a prefix
    reshaped_df.columns = ["quadkey"] + [
        f"raster_{int(col)}" if not pd.isnull(col) else col
        for col in reshaped_df.columns[1:]
    ]

    # print("---After reshaping---")
    # print(reshaped_df.head())
    # print(reshaped_df.tail())
    # print(reshaped_df.columns)
    # print(reshaped_df.shape)
    # print(reshaped_df.info())

    # Count the number of unique quadkey values in the DataFrame
    # unique_quadkey_count = df["quadkey"].nunique()
    # print(unique_quadkey_count)

    return reshaped_df


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
    # TODO: Fix out of memory problem by using dask https://tutorial.xarray.dev/intermediate/xarray_and_dask.html
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
    data_slice_male_quadkey = load_male_dataset()
    # pprint.pprint(zoom_level_2)
    # pprint.pprint(zoom_level_13)
