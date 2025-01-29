import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter
import xyzservices.providers as xyz
import requests
from io import BytesIO

class MapView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.tile_provider = xyz.USGS.USImagery
        self.tile_size = 256
        self.zoom_level = 2
        self.center_tile = (0, 0)  # Tile at (0, 0) represents the map center
        self.tiles = {}  # Cache for loaded tiles

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.draw_tiles()


    def draw_tiles(self):
        self.scene.clear()
        self.tiles = {}

        # Calculate tile range based on view size
        view_width = self.viewport().width()
        view_height = self.viewport().height()

        center_x, center_y = self.center_tile

        left = center_x - view_width // (2 * self.tile_size)
        right = center_x + view_width // (2 * self.tile_size)
        top = center_y - view_height // (2 * self.tile_size)
        bottom = center_y + view_height // (2 * self.tile_size)

        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                pixmap = self.get_tile(x, y)
                if pixmap:
                    item = QGraphicsPixmapItem(pixmap)
                    item.setPos(x * self.tile_size, y * self.tile_size)
                    self.scene.addItem(item)

    def get_tile(self, x, y):
        if (x, y) in self.tiles:
            return self.tiles[(x, y)]

        url = self.tile_provider.build_url(x=x, y=y, z=self.zoom_level)
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = QPixmap()
            image.loadFromData(BytesIO(response.content).read())
            self.tiles[(x, y)] = image
            return image
        except Exception as e:
            print(f"Failed to load tile ({x}, {y}): {e}")
            return None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.draw_tiles()

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle > 0 and self.zoom_level < 19:
            self.zoom_level += 1
        elif angle < 0 and self.zoom_level > 0:
            self.zoom_level -= 1

        self.draw_tiles()

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Map Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.map_view = MapView()
        self.setCentralWidget(self.map_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapApp()
    window.show()
    sys.exit(app.exec_())
