import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import sys, os, glob, shutil, time, re


# Set path to the root directory
sys.path.append('../')

# Step 1: Load bus stop data (CSV)
# Assuming your bus stop data is in a CSV file with columns: latitude, longitude, trip_count
bus_stop_data = pd.read_csv('data/processed/gtfs_output.csv')

# Step 2: Convert bus stop data to GeoDataFrame
geometry = [Point(xy) for xy in zip(bus_stop_data['stop_lon'], bus_stop_data['stop_lat'])]
bus_stop_gdf = gpd.GeoDataFrame(bus_stop_data, geometry=geometry, crs="EPSG:4326")

# Step 3: Load LGA shapefile (assuming LGA shapefile has LGA_CODE and LGA_NAME)
lga_gdf = gpd.read_file('data/raw/LGA_POLYGON.shp')

# Ensure both GeoDataFrames have the same CRS
if bus_stop_gdf.crs != lga_gdf.crs:
    lga_gdf = lga_gdf.to_crs(bus_stop_gdf.crs)

# Step 4: Perform spatial join to assign each bus stop to an LGA
bus_stops_in_lga = gpd.sjoin(bus_stop_gdf, lga_gdf, how="left", predicate="intersects")

# Step 5: Group by LGA_CODE and LGA_NAME, and sum the trip_count
lga_trip_sum = bus_stops_in_lga.groupby(['LGA_CODE', 'LGA_NAME'])['count'].sum().reset_index()

# Step 6: Rename columns for clarity
lga_trip_sum.columns = ['LGA_CODE', 'LGA_NAME', 'sum_ptv_trips']

# Step 7: Write the DataFrame to a CSV file
lga_trip_sum.to_csv('data/processed/lga_trip_counts.csv', index=False)

print("Trip count per LGA has been written to 'lga_trip_counts.csv'")
