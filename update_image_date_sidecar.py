import json
from datetime import datetime, timezone
import re
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_sidecar_with_filename_date(json_path):
    if not os.path.isfile(json_path):
        logging.error(f"File not found: {json_path}")
        return

    # Load the sidecar JSON with explicit UTF-8 encoding
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        logging.error(f"Failed to read {json_path}: {e}")
        return

    # Extract image file name from title
    image_title = data.get('title')
    if not image_title:
        logging.error(f"No 'title' field found in JSON for {json_path}.")
        return

    logging.info(f"Processing: {image_title}")

    # Extract date from filename using regex (expecting IMG-YYYYMMDD-*.jpg)
    match = re.search(r'(\d{4})(\d{2})(\d{2})', image_title)
    if not match:
        logging.warning(f"No date found in 'title' field for {json_path}. Skipping update.")
        return

    year, month, day = map(int, match.groups())

    # Build datetime objects for taken and creation times
    taken_time = datetime(year, month, day, 8, 6, 38, tzinfo=timezone.utc)
    creation_time = datetime(year, month, day, 22, 54, 5, tzinfo=timezone.utc)

    # Convert to timestamps
    taken_timestamp = int(taken_time.timestamp())
    creation_timestamp = int(creation_time.timestamp())

    # Format the readable string
    taken_formatted = taken_time.strftime("%d %b %Y, %H:%M:%S UTC")
    creation_formatted = creation_time.strftime("%d %b %Y, %H:%M:%S UTC")

    # Update JSON fields
    data['photoTakenTime'] = {
        "timestamp": str(taken_timestamp),
        "formatted": taken_formatted
    }
    data['creationTime'] = {
        "timestamp": str(creation_timestamp),
        "formatted": creation_formatted
    }

    # Write back updated JSON
    try:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        logging.info(f"Updated {json_path} with date {year}-{month:02}-{day:02}")
    except Exception as e:
        logging.error(f"Failed to write {json_path}: {e}")

# Process a folder of JSON files
def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        logging.error(f"Folder not found: {folder_path}")
        return

    # Loop through files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg.supplemental-metadata.json") or filename.endswith(".mp4.supplemental-metadata.json") or filename.endswith(".jpeg.supplemental-metadata.json"):
            json_path = os.path.join(folder_path, filename)
            update_sidecar_with_filename_date(json_path)

# Example usage via CLI argument
if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python script.py path_to_folder_or_file")
    else:
        # Check if it's a folder or file
        path = sys.argv[1]
        if os.path.isdir(path):
            process_folder(path)
        elif os.path.isfile(path):
            update_sidecar_with_filename_date(path)
        else:
            logging.error(f"Invalid path: {path}")
