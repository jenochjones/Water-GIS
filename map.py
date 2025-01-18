from pyproj import CRS
from pyproj import Transformer
from xyzservices import providers



def convert_to_wgs(self, coords):
    transformer = Transformer.from_crs(f"EPSG:{self.crs}", "EPSG:4326", always_xy=True)
    converted_coords = transformer.transform(*coords)
    return converted_coords


def is_valid_epsg(epsg_code):
    try:
        # Attempt to create a CRS object from the EPSG code
        crs = CRS.from_epsg(epsg_code)
        return True
    except Exception as e:
        # If an error occurs, the EPSG code is not valid
        return False
