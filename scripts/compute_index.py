import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import sys, os, glob, shutil, time, re
import numpy as np

# Set path to the root directory
sys.path.append('../')

def remove_words_in_parentheses(s):
    return re.sub(r'\([^)]*\)', '', s).strip()


def remove_last_word(s):
    words = s.split()  # Split the string into words
    return ' '.join(words[:-1])  # Join all but the last word

# Read the excel file with population data in sheet Total_Households and store it in a pandas DataFrame, ignoring the first 9 rows
population_data = pd.read_excel('data/raw/VIF2023_LGA_Pop_Hhold_Dwelling_Projections_to_2036.xlsx', sheet_name='Total_Households', skiprows=9)

# Rename the columns for clarity: LGA code to LGA_CODE, and LGA name to LGA_NAME
population_data.rename(columns={'LGA  code': 'LGA_CODE', 'LGA': 'LGA_NAME'}, inplace=True)

# For each value of LGA_NAME, make the string uppercase and remove the characters after the first space
population_data['LGA_NAME'] = population_data['LGA_NAME'].str.upper().apply(remove_words_in_parentheses)

# Display the first few rows of the population data
print(population_data.head())

# Read the csv file with sum_ptv_trips data and store it in a pandas DataFrame
trip_data = pd.read_csv('data/processed/lga_trip_counts.csv')

# Display the first few rows of the trip data
print(trip_data.head())

# Merge the population data with the trip data based on LGA_CODE
merged_data = population_data.merge(trip_data, on='LGA_NAME', how='left')

# Typecast all column names to string
merged_data.columns = merged_data.columns.astype(str)

# print the columns of the merged data
print(merged_data.columns)

# Display the first few rows of the merged data
print(merged_data.head())

# Calculate the ratio of total bus trips to total households and store it in a new column 'trip_household_ratio_index'
merged_data['trip_household_ratio_index'] = merged_data['sum_ptv_trips'] / merged_data['2021']

# Normalize the 'trip_household_ratio_index' column and bring to a scale of 0 to 100
merged_data['trip_household_ratio_index'] = (merged_data['trip_household_ratio_index'] - merged_data['trip_household_ratio_index'].min()) / (merged_data['trip_household_ratio_index'].max() - merged_data['trip_household_ratio_index'].min()) * 100

# Display the first few rows of the merged data with the new column
print(merged_data.head())

# Save the merged data with the new column to a csv file
merged_data.to_csv('data/final/trip_household_ratio_index.csv', index=False)

