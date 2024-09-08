# Script to merge the population census data on SA2 level with the VIC shapefile and GTFS data on bus stops
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import sys, os, glob, shutil, time, re
import numpy as np
import matplotlib.pyplot as plt


# Set path to the root directory
sys.path.append('../')

# Step 1: Load the population census data
pop_data = pd.read_csv('data/raw/2021_GCP_SA2_for_VIC_short-header/2021 Census GCP Statistical Area 2 for VIC/2021Census_G01_VIC_SA2.csv')
# keep only the columns we need: SA2_CODE_2021, and Tot_P_P
pop_data = pop_data[['SA2_CODE_2021', 'Tot_P_P']]

# Preview the population data
print(pop_data.head())

# Step 2: Load the SA2 shapefile
sa2_gdf = gpd.read_file('data/raw/SA2_2021_AUST_SHP_GDA2020/SA2_2021_AUST_GDA2020.shp')

# Keep only the columns we need: SA2_CODE21, SA2_NAME21, and geometry
sa2_gdf = sa2_gdf[['SA2_CODE21', 'SA2_NAME21', 'STE_CODE21', 'geometry']]

# Preview the SA2 shapefile
print(sa2_gdf.head())

# Step 3: Merge the population data with the SA2 shapefile based on SA2_CODE_2021
# First make sure the columns are of the same type
pop_data['SA2_CODE_2021'] = pop_data['SA2_CODE_2021'].astype(str)
sa2_gdf['SA2_CODE21'] = sa2_gdf['SA2_CODE21'].astype(str)

sa2_gdf = sa2_gdf.merge(pop_data, left_on='SA2_CODE21', right_on='SA2_CODE_2021', how='left')

# Remove rows with missing values
sa2_gdf = sa2_gdf.dropna(subset=['Tot_P_P']).reset_index(drop=True)

# Preview the merged data
print(sa2_gdf.head())

# Plot the map, color-coding the polygons by population
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot the SA2 polygons and color them by the 'Tot_P_P'
sa2_gdf.plot(column='Tot_P_P', ax=ax, legend=True, cmap='OrRd',
             legend_kwds={'label': "Total Population by SA2",
                          'orientation': "horizontal"})
# Add a title
ax.set_title('Population by SA2', fontsize=15)

# Remove axis for cleaner visualization
ax.set_axis_off()

# Save the plot to a file
fig.savefig('data/processed/population_by_sa2_map.png', dpi=300)
print("Map of population by SA2 has been saved to 'population_by_sa2_map.png'")

# Step 4: Load the bus stop data (CSV)
bus_stop_data = pd.read_csv('data/processed/gtfs_output.csv')

# Step 5: Convert bus stop data to GeoDataFrame
geometry = [Point(xy) for xy in zip(bus_stop_data['stop_lon'], bus_stop_data['stop_lat'])]

bus_stop_gdf = gpd.GeoDataFrame(bus_stop_data, geometry=geometry, crs="EPSG:4326")

# Ensure both GeoDataFrames have the same CRS
if bus_stop_gdf.crs != sa2_gdf.crs:
    bus_stop_gdf = bus_stop_gdf.to_crs(sa2_gdf.crs)


# Step 6: Perform spatial join to assign each bus stop to an SA2
bus_stops_in_sa2 = gpd.sjoin(bus_stop_gdf, sa2_gdf, how="left", predicate="intersects")

# Step 7: Group by SA2_CODE21 and SA2_NAME21, and count the number of bus stops
sa2_bus_stop_count = bus_stops_in_sa2.groupby(['SA2_CODE21', 'SA2_NAME21'])['count'].sum().reset_index()

# Step 8: Rename columns for clarity
sa2_bus_stop_count.columns = ['SA2_CODE21', 'SA2_NAME21', 'sum_ptv_trips']

# Preview the bus stop count data
print("\nBus stop count per SA2:")
print(sa2_bus_stop_count.head())

# Step 9: Write the DataFrame to a CSV file
sa2_bus_stop_count.to_csv('data/processed/sa2_bus_stop_count.csv', index=False)

print("Bus stop count per SA2 has been written to 'sa2_bus_stop_count.csv'")

# Step 10: Compute the bus stop density by dividing the number of bus stops by the population
sa2_gdf = sa2_gdf.merge(sa2_bus_stop_count, on='SA2_CODE21', how='left')

sa2_gdf['bus_stop_density'] = 100 * (sa2_gdf['sum_ptv_trips'].astype(float) / sa2_gdf['Tot_P_P'].astype(float))
print(sa2_gdf[['sum_ptv_trips', 'Tot_P_P']].dtypes)



# Step 11: Normalize the 'bus_stop_density' column and bring to a scale of 0 to 100
sa2_gdf['bus_stop_density'] = (sa2_gdf['bus_stop_density'] - sa2_gdf['bus_stop_density'].min()) / (sa2_gdf['bus_stop_density'].max() - sa2_gdf['bus_stop_density'].min()) * 100

# Preview the data with the new column
print("\nData with bus stop density:")
print(sa2_gdf.head(10))

# Step 12: Save the merged data with the new column to a csv file
# sa2_gdf.to_excel('data/final/bus_stop_density_by_sa2.xlsx', index=False)

print("Bus stop density by SA2 has been saved to 'bus_stop_density_by_sa2.xlsx'")

# Read this excel to gdf
df = pd.read_excel('data/final/bus_stop_density_by_sa2.xlsx')

# substitue the column 'bus_stop_density' in sa2_gdf with that in df
sa2_gdf['bus_stop_density'] = df['bus_stop_density']

# Step 13: Plot the map, color-coding the polygons by bus_stop_density
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot the SA2 polygons and color them by the 'bus_stop_density'
sa2_gdf.plot(column='bus_stop_density', ax=ax, legend=True, cmap='OrRd',
             legend_kwds={'label': "Transit Equity Index (population) by SA2",
                          'orientation': "horizontal"})

# Add a title
ax.set_title('Transit Equity Index (population) by SA2', fontsize=15)

# Remove axis for cleaner visualization
ax.set_axis_off()

# Save the plot to a file
fig.savefig('data/processed/bus_stop_density_by_sa2_map.png', dpi=500)

print("Map of bus stop density by SA2 has been saved to 'bus_stop_density_by_sa2_map.png'")

# Display the plot
plt.show()
