import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QToolBar, QPushButton, QGraphicsPixmapItem, QLabel, QStatusBar
)
from PyQt5.QtCore import Qt, QRectF, QSize, QPointF
from PyQt5.QtGui import QPainter, QIcon, QPixmap
import xyzservices.providers as xyz
import requests
import math
from io import BytesIO


class MapView(QGraphicsView):
    def __init__(self, scene, status_label):
        super().__init__()
        self.scene = scene
        self.status_label = status_label
        self.setScene(self.scene)

        self.tile_provider = xyz.USGS.USImagery
        self.tile_size = 256
        self.zoom_level = 0
        self.center_lon = 0
        self.center_lat = 0
        self.tiles = {}

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.draw_tiles()

    def lonlat_to_tile(self, lon, lat, zoom):
        """Convert lon/lat to tile x/y at a given zoom level."""
        n = 2 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
        return xtile, ytile

    def tile_to_lonlat(self, x, y, zoom):
        """Convert tile x/y back to lon/lat."""
        n = 2 ** zoom
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_deg = math.degrees(lat_rad)
        return lon_deg, lat_deg

    def draw_tiles(self):
        self.scene.clear()
        self.tiles = {}

        view_rect = self.viewport().rect()
        width = view_rect.width()
        height = view_rect.height()

        center_x_tile, center_y_tile = self.lonlat_to_tile(self.center_lon, self.center_lat, self.zoom_level)
        tiles_across = width // self.tile_size + 2
        tiles_down = height // self.tile_size + 2

        start_x = center_x_tile - tiles_across // 2
        start_y = center_y_tile - tiles_down // 2
        end_x = start_x + tiles_across
        end_y = start_y + tiles_down

        max_tile_index = 2 ** self.zoom_level - 1

        for dx, x in enumerate(range(start_x, end_x)):
            if x < 0 or x > max_tile_index:
                continue
            for dy, y in enumerate(range(start_y, end_y)):
                if y < 0 or y > max_tile_index:
                    continue

                pixmap = self.get_tile(x, y, self.zoom_level)
                if pixmap:
                    item = QGraphicsPixmapItem(pixmap)
                    item.setPos(dx * self.tile_size, dy * self.tile_size)
                    self.scene.addItem(item)

        self.scene.setSceneRect(0, 0, tiles_across * self.tile_size, tiles_down * self.tile_size)


    def get_tile(self, x, y, z):
        if (x, y, z) in self.tiles:
            return self.tiles[(x, y, z)]

        url = self.tile_provider.build_url(x=x, y=y, z=z)
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = QPixmap()
            image.loadFromData(BytesIO(response.content).read())
            self.tiles[(x, y, z)] = image
            return image
        except Exception as e:
            print(f"Failed to load tile ({x}, {y}, {z}): {e}")
            return None

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_level = min(self.zoom_level + 1, 18)
        else:
            self.zoom_level = max(self.zoom_level - 1, 1)

        self.draw_tiles()

    def mouseMoveEvent(self, event):
        point = self.mapToScene(event.pos())
        view_rect = self.viewport().rect()
        center_tile_x, center_tile_y = self.lonlat_to_tile(self.center_lon, self.center_lat, self.zoom_level)
        offset_x = point.x() - self.scene.width() / 2
        offset_y = point.y() - self.scene.height() / 2

        lon_per_pixel = 360.0 / (2 ** self.zoom_level * self.tile_size)
        lat_per_pixel = lon_per_pixel  # Approximate, better for small areas

        lon = self.center_lon + offset_x * lon_per_pixel
        lat = self.center_lat - offset_y * lat_per_pixel

        self.status_label.setText(f"Lat: {lat:.5f}, Lon: {lon:.5f}")
        super().mouseMoveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Viewer")
        self.resize(800, 600)

        self.scene = QGraphicsScene(self)
        self.status_label = QLabel("Lat: , Lon: ")
        self.statusBar = QStatusBar()
        self.statusBar.addPermanentWidget(self.status_label)
        self.setStatusBar(self.statusBar)

        self.MapView = MapView(self.scene, self.status_label)
        self.setCentralWidget(self.MapView)

        self.create_toolbars()

    def create_toolbars(self):
        toolbars = {
            "File Toolbar": [("icons/new_proj.png", "Ctrl+N"),
                             ("icons/open.png", "Ctrl+O"),
                             ("icons/save.png", "Ctrl+S")],
            "Run Toolbar": [("icons/crs.png", None),
                            ("icons/run.png", "Ctrl+R")],
            "Analysis Toolbar": [("icons/graph.png", None)],
            "Draw Toolbar": [("icons/select.png", None),
                             ("icons/add_node.png", None)],
        }

        for name, buttons in toolbars.items():
            toolbar = QToolBar(name, self)
            self.addToolBar(toolbar)
            for icon_path, shortcut in buttons:
                btn = QPushButton(QIcon(icon_path), "", self)
                btn.setIconSize(QSize(35, 35))
                if shortcut:
                    btn.setShortcut(shortcut)
                toolbar.addWidget(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
