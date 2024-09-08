import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import sys, os, glob, shutil, time, re


# Set path to the root directory
sys.path.append('../')

# Step 1: Load the LGA shapefile
lga_gdf = gpd.read_file('data/raw/LGA_POLYGON.shp')

# Step 2: Load the CSV with LGA trip counts
lga_trip_sum = pd.read_csv('data/final/trip_household_ratio_index.csv')

# Remove the 'Unnamed: 0' column and 'LGA_CODE_y' null values
lga_trip_sum = lga_trip_sum.drop(columns=['Unnamed: 0'])
lga_trip_sum = lga_trip_sum.dropna(subset=['LGA_CODE_y'])


# Ensure that both LGA_CODE columns are strings for merging
lga_gdf['LGA_CODE'] = lga_gdf['LGA_CODE'].astype(str)
lga_trip_sum['LGA_CODE_y'] = lga_trip_sum['LGA_CODE_y'].astype(int).astype(str)

# Step 3: Merge the trip count data with the LGA shapefile based on LGA_CODE
lga_gdf = lga_gdf.merge(lga_trip_sum, left_on='LGA_CODE', right_on='LGA_CODE_y', how='left')

# Step 4: Plot the map, color-coding the polygons by trip_household_ratio_index
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot the LGA polygons and color them by the 'trip_household_ratio_index'
lga_gdf.plot(column='trip_household_ratio_index', ax=ax, legend=True, cmap='OrRd', 
             legend_kwds={'label': "Transit Equity Index (dwelling)",
                          'orientation': "horizontal"})

# Add a title
ax.set_title('Transit Equity Index (dwelling)', fontsize=15)

# Remove axis for cleaner visualization
ax.set_axis_off()

# Save the plot to a file
fig.savefig('data/processed/lga_trip_counts_map.png', dpi=300)
print("Map of total bus trips by LGA has been saved to 'lga_trip_counts_map.png'")

# Display the plot
plt.show()
