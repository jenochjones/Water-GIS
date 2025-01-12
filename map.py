import folium
import io


def initialize_map(self):

    if self.project:
        center_point = self.junctions.geometry.union_all().centroid
        center_location = [center_point.x, center_point.y]
    else:
        center_location = [0, 0]

    # Create a Folium map centered at a default location
    folium_map = folium.Map(location=center_location, zoom_start=10, control_scale=True, tiles=None)

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