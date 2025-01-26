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
    # The smaller the bounding box, the higher the zoom level
    num_tiles = 10
    lon_diff = abs(lon_max - lon_min)
    zoom = max(0, min(max_zoom, int(math.floor((math.log(360 * num_tiles) - math.log(lon_diff)) / math.log(2)))))#zoom = int(min(max_zoom, max(0, (max_zoom - 1) - math.log2(max(lat_diff, lon_diff) + 1e-9))))  # Clamp between 0 and 19
    return zoom

# Function to retrieve and combine tiles
def get_wms_tiles(lat_min, lon_min, lat_max, lon_max, provider=xyz.USGS.USImagery):
    # Calculate zoom level
    zoom = calculate_zoom(lat_min, lon_min, lat_max, lon_max, provider.max_zoom)

    # Get tile coordinates for bounding box
    x_min, y_min = latlon_to_tile(lat_max, lon_min, zoom)
    x_max, y_max = latlon_to_tile(lat_min, lon_max, zoom)

    # Fetch and combine tiles
    tiles = []
    for y in range(y_min, y_max + 1):
        row = []
        for x in range(x_min, x_max + 1):
            
            url = provider.build_url(x=x, y=y, z=zoom)
            response = requests.get(url)
            if response.status_code == 200:
                tile = Image.open(BytesIO(response.content))
                row.append(tile)
            else:
                row.append(Image.new('RGB', (256, 256), (255, 255, 0)))  # Blank tile for failed requests
            
            print(f'{round(((((y - y_min) * (x_max - x_min)) + (x - x_min)) * 100) / ((y_max - y_min + 1) * (x_max - x_min + 1)), 1)}% Complete')
        tiles.append(row)

    return tiles

