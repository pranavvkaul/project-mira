import json
from fastapi import FastAPI
import os

FILE_PATHS = [
    'Case Study 3 JSON 1.txt',
    'Case Study 3 JSON 2.txt',
    'Case Study 3 JSON 3.txt'
]

def load_and_merge_data(file_paths):
    final_data_map = {}

    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                data_list = json.load(f)

            for item in data_list:
                property_id = item.get("id")

                if property_id is not None:
                    if property_id not in final_data_map:
                        final_data_map[property_id] = {}

                    final_data_map[property_id].update(item)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading or parsing {file_path}: {e}")
            pass 

    final_list = list(final_data_map.values())
    return final_list

FULL_PROPERTY_DATA = load_and_merge_data(FILE_PATHS)

app = FastAPI()

@app.get("/all-properties")
def get_all_merged_properties():
    """
    Returns the single, merged list of properties as a JSON array.
    """
    return FULL_PROPERTY_DATA