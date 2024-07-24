"""
fetch_data.py

This module contains functions for fetching and processing data from the Antares API.
"""

import ctypes
import json
from datetime import datetime
import requests

def decompress(data):
    """
    Decompresses compressed data using the Unishox2 decompression library.

    Args:
        data (str): Hexadecimal string of compressed data.

    Returns:
        dict: Decompressed data as a Python dictionary.
    """
    # Load the shared library (decompress library)
    lib = ctypes.CDLL('./libunishox2.dll')  # Change to 'libunishox2.dll' on Windows

    # Define the Unishox2 decompress function signature
    lib.unishox2_decompress_simple.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
    lib.unishox2_decompress_simple.restype = ctypes.c_int

    compressed_data = bytes.fromhex(data)

    # Allocate a buffer for the decompressed data
    decompressed_data = ctypes.create_string_buffer(1024)  # Adjust size as needed

    # Decompress the data
    decompressed_length = lib.unishox2_decompress_simple(
        compressed_data,
        len(compressed_data),
        decompressed_data
    )

    # Get the decompressed data as a string
    decompressed_string = decompressed_data.raw[:decompressed_length].decode('utf-8')

    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(decompressed_string)

    return data_dict

def fetch_data_api_antares(device_id, url, headers, last_time):
    """
    Fetches data from the Antares API.

    Args:
        device_id (str): Device ID.
        url (str): URL of the API endpoint.
        headers (dict): Headers for the API request.
        last_time (datetime.datetime): Last processed time.

    Returns:
        list: List of JSON objects containing fetched data.
    """
    # Send GET request with timeout
    response = requests.get(url, headers=headers, timeout=10)

    # Check if request was successful
    if response.status_code == 200:

        # Parse JSON response
        data = response.json()

        # Create an array to store the JSON objects
        json_array = []

        # Filter entries with the current date (only date part)
        for entry in data["m2m:list"]:
            # Get the creation time
            creation_time_str = entry["m2m:cin"]["ct"]
            creation_time = datetime.strptime(creation_time_str, "%Y%m%dT%H%M%S")

            # Continue to the next entry if the creation time is before the last processed time
            if creation_time <= last_time:
                continue

            con_data = entry["m2m:cin"]["con"]
            # Check if the data is JSON
            try:
                con_data_json = json.loads(con_data)
                # Check if the data contains a "data" key
                if "data" in con_data_json:
                    data_value = con_data_json["data"]
                    # Check if data needs to be decompressed
                    decompressed_data = decompress(data_value)

                    json_object = {
                        'time': creation_time,
                        'device_id': device_id,
                        'temp': decompressed_data.get('temp', None),
                        'ph': decompressed_data.get('ph', None),
                        'tds': decompressed_data.get('tds', None),
                        'do': decompressed_data.get('do', None),
                        'orp': decompressed_data.get('orp', None),
                        'salinity': decompressed_data.get('salinity', None),
                        'water_h': decompressed_data.get('water_h', None),
                        'water_cl': decompressed_data.get('water_cl', None)
                    }

                    # Append the JSON object to the array
                    json_array.append(json_object)
                else:
                    print("Skipping data without 'data' key:", con_data)
            except json.JSONDecodeError:
                print("Skipping non-JSON data:", con_data)

    else:
        print("Failed to fetch data. Status code:", response.status_code)

    return json_array
