import math
import requests
from io import BytesIO
from PIL import Image
import xyzservices.providers as xyz

# Function to convert latitude/longitude to tile numbers
def latlon_to_tile(lat, lon, zoom):
    n = 2 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    return x_tile, y_tile

# Function to calculate an appropriate zoom level based on bounding box size
def calculate_zoom(lat_min, lon_min, lat_max, lon_max, max_zoom):
    num_tiles = 10
    lon_diff = abs(lon_max - lon_min)
    zoom = max(0, min(max_zoom, int(math.floor((math.log(360 * num_tiles) - math.log(lon_diff)) / math.log(2)))))
    return zoom

# Function to retrieve, combine tiles, and save as a single image
def get_and_save_combined_image(lat_min, lon_min, lat_max, lon_max, filepath, provider=xyz.USGS.USImagery):
    # Calculate zoom level
    zoom = calculate_zoom(lat_min, lon_min, lat_max, lon_max, provider.max_zoom)

    # Get tile coordinates for bounding box
    x_min, y_min = latlon_to_tile(lat_max, lon_min, zoom)
    x_max, y_max = latlon_to_tile(lat_min, lon_max, zoom)

    # Tile dimensions
    tile_width, tile_height = 256, 256

    # Calculate dimensions of the final image
    image_width = (x_max - x_min + 1) * tile_width
    image_height = (y_max - y_min + 1) * tile_height

    # Create a blank image to hold all tiles
    combined_image = Image.new('RGB', (image_width, image_height))

    # Fetch and paste tiles into the combined image
    for y in range(y_min, y_max + 1):
        for x in range(x_min, x_max + 1):
            url = provider.build_url(x=x, y=y, z=zoom)
            response = requests.get(url)
            if response.status_code == 200:
                tile = Image.open(BytesIO(response.content))
            else:
                tile = Image.new('RGB', (tile_width, tile_height), (255, 255, 0))  # Blank tile for failed requests

            # Calculate position to paste the tile
            x_offset = (x - x_min) * tile_width
            y_offset = (y - y_min) * tile_height
            combined_image.paste(tile, (x_offset, y_offset))

            # Progress update
            progress = round(((((y - y_min) * (x_max - x_min + 1)) + (x - x_min + 1)) * 100) / ((y_max - y_min + 1) * (x_max - x_min + 1)), 1)
            print(f"{progress}% Complete")

    # Save the combined image as a JPEG file
    combined_image.save(filepath, "JPEG")
    print(f"Image saved to {filepath}")

# Example usage
lat_min, lon_min = 40.0, -112.0
lat_max, lon_max = 41.0, -111.0
filepath = "./img/combined_image.jpg"
get_and_save_combined_image(lat_min, lon_min, lat_max, lon_max, filepath)
