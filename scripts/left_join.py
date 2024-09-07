import pandas as pd
import sys, os, json, argparse, time
import numpy as np

# Set path to the root directory
sys.path.append('../')

# Constants
ROOT_DATA_DIR = './data/raw/gtfs/'
PATH_STOP = 'google_transit/stops.txt'
PATH_STOP_TIMES = 'google_transit/stop_times.txt'

def load_data(path):
    # Load data from txt file
    data = pd.read_csv(path)
    return data

def save_data(data, path):
    # Save data to csv file
    data.to_csv(path, index=False)

def merge_data(df_stop_times, df_stops):
    # Right join data1 and data2 on 'stop_id'
    merged = pd.merge(df_stop_times, df_stops, on='stop_id', how='left')
    return merged


def main():
    # Empty pandas dataframe to concatenate all merged data
    merged_data = []

    # Iterate over all folders in the root data directory, not including hidden files
    for path, folders, files in os.walk(ROOT_DATA_DIR):
        print(folders)
        for folder in folders:
            # Load data
            stop_times = load_data(os.path.join(ROOT_DATA_DIR, folder, PATH_STOP_TIMES))
            stops = load_data(os.path.join(ROOT_DATA_DIR, folder, PATH_STOP))

            print(stop_times.head())
            print(stops.head())

            # Merge data
            merged = merge_data(stop_times, stops)

            # Concatenate data
            merged_data.append(merged)
        break

    # Concatenate all data
    merged_data = pd.concat(merged_data)

    # Group by stop_id and find the count of unique stop_id
    grouped = merged_data.groupby(['stop_id', 'stop_lat', 'stop_lon']).size().reset_index(name='count')

    print(grouped.head())

    # Save data
    save_data(grouped, './data/processed/gtfs_output.csv')

if __name__ == '__main__':
    main()
