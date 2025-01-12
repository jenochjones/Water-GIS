import folium
import io
from pyproj import CRS


def is_valid_epsg(epsg_code):
    try:
        # Attempt to create a CRS object from the EPSG code
        crs = CRS.from_epsg(epsg_code)
        return True
    except Exception as e:
        # If an error occurs, the EPSG code is not valid
        return False


def initialize_map(self):

    if self.project:
        center_point = self.junctions.geometry.union_all().centroid
        center_location = [center_point.x, center_point.y]
        bounds = self.junctions.total_bounds  # Returns [minx, miny, maxx, maxy]
        format_bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
    else:
        center_location = [0, 0]
        format_bounds = None

    if self.crs:
        folium_map = folium.Map(location=center_location, zoom_start=12, control_scale=True)
        folium.TileLayer(
            'OpenStreetMap',
            name='OpenStreetMap',
            attr='© OpenStreetMap contributors'
        ).add_to(folium_map)  # OpenStreetMap (default)

        folium.TileLayer(
            'CartoDB positron',
            name='CartoDB Positron',
            attr='© OpenStreetMap contributors, © CartoDB'
        ).add_to(folium_map)  # CartoDB Positron (light map)

        folium.TileLayer(
            'CartoDB dark_matter',
            name='CartoDB Dark Matter',
            attr='© OpenStreetMap contributors, © CartoDB'
        ).add_to(folium_map)  # CartoDB Dark Matter (dark map)

        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
            name='ESRI World Imagery',
            overlay=False,
            control=True
        ).add_to(folium_map)  # ESRI World Imagery (aerial imagery)

        folium.LayerControl().add_to(folium_map) # Add a layer control to allow switching between basemaps
    else:
        folium_map = folium.Map(location=center_location, zoom_start=12, control_scale=True, tiles=None)

    if format_bounds:
        folium_map.fit_bounds(format_bounds)
    
    data = io.BytesIO()

     # Add the line feature to the map
    for _, row in self.pipes.iterrows():
        folium.PolyLine(
            locations=[[coord[1], coord[0]] for coord in row.geometry.coords],
            color='red',
            weight=3,
            popup=''
        ).add_to(folium_map)

    for _, row in self.junctions.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.8,
            popup=''
        ).add_to(folium_map)

    folium_map.save(data, close_file=False)
    self.map_view.setHtml(data.getvalue().decode())

    self.statusBar().showMessage("Map loaded.")