import os
import requests
import xml.etree.ElementTree as ET
import argparse
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime

# Set up argument Parser
parser = argparse.ArgumentParser(description="Download MP3 files from an XML file.")
parser.add_argument("xml_file", help="Path to the XML file containing podcast data.")
parser.add_argument("output_base_dir", nargs='?', default='output', help="Base directory to save downloaded MP3 files. (default: output)")
args = parser.parse_args()

# Path to the XML file
xml_file = args.xml_file

# Output directory
output_base_dir = args.output_base_dir

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Extract the channel title (assuming it's in the <title> tag under the root element)
channel_title = root.find("channel/title").text if root.find("channel/title") is not None else "unknown_channel"

# Iterate through the XML to find MP3 URLs and titles
for item in root.findall(".//item"):
    item_title = item.find("title").text if item.find("title") is not None else "unknown_item"
    mp3_url = item.find("enclosure").attrib.get("url") if item.find("enclosure") is not None else None
    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else None

    # Parse pubDate to get year, month, day
    if pub_date:
        try:
            dt = parsedate_to_datetime(pub_date)
            date_prefix = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}_"
        except Exception:
            date_prefix = ""
    else:
        date_prefix = ""

    # Prepend date to item_title for output directory
    dated_item_title = f"{date_prefix}-{item_title}"

    if mp3_url:
        # Parse the URL to get the path without query parameters
        parsed_url = urlparse(mp3_url)
        file_name = os.path.basename(parsed_url.path)

        # Create a directory for the channel and item title (with date prefix)
        item_dir = os.path.join(output_base_dir, channel_title, dated_item_title)
        os.makedirs(item_dir, exist_ok=True)

        file_path = os.path.join(item_dir, file_name)

        # Skip download if file already exists
        if os.path.exists(file_path):
            print(f"Already exists, skipping: {file_path}")
            continue

        # Download the MP3 file
        print(f"Downloading {mp3_url} to {file_path}...")
        response = requests.get(mp3_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Saved: {file_path}")
        else:
            print(f"Failed to download: {mp3_url} (Status code: {response.status_code})")