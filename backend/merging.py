import json
from fastapi import FastAPI
import os

# List of paths for the raw data files that need to be merged.
# These simulate data fetched from different sources (e.g., scraping APIs).
FILE_PATHS = [
    'Case Study 3 JSON 1.txt',
    'Case Study 3 JSON 2.txt',
    'Case Study 3 JSON 3.txt'
]

def load_and_merge_data(file_paths):
    """
    Loads data from multiple JSON files, merges property records based on their 
    'id', and returns a single list of complete property dictionaries.
    """
    final_data_map = {}

    for file_path in file_paths:
        try:
            # 1. Open and load the JSON data from the current file path
            with open(file_path, 'r') as f:
                data_list = json.load(f)

            for item in data_list:
                property_id = item.get("id")

                if property_id is not None:
                    # Initialize an entry for the ID if it doesn't exist
                    if property_id not in final_data_map:
                        final_data_map[property_id] = {}

                    # Merge new data into the existing dictionary for that ID.
                    # This handles data enrichment (e.g., adding an amenity list 
                    # from one file to a base record from another).
                    final_data_map[property_id].update(item)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Log the error but continue processing the remaining files
            print(f"Error loading or parsing {file_path}: {e}")
            pass 

    # Convert the map of merged properties back into a list of dictionaries
    final_list = list(final_data_map.values())
    return final_list

# Execute the merging process immediately on script load.
# The result is stored as a global variable.
FULL_PROPERTY_DATA = load_and_merge_data(FILE_PATHS)

# Initialize FastAPI application instance.
app = FastAPI()

@app.get("/all-properties")
def get_all_merged_properties():
    """
    API endpoint to return the complete, merged list of properties.
    This can be used for debugging or by a separate frontend data grid.
    """
    return FULL_PROPERTY_DATA
