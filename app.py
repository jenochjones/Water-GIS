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


def mercator_to_latlon(x, y):
        lon = x * 180 / 20037508.34
        lat = y * 180 / 20037508.34
        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
        return lat, lon


class MapView(QGraphicsView):
    def __init__(self, scene, status_label):
        super().__init__()
        self.scene = scene
        self.status_label = status_label
        self.setScene(self.scene)

        self.tile_provider = xyz.USGS.USImagery
        self.tile_size = 256
        self.zoom_level = 0
        self.tiles = {}

        # Web Mercator limits in meters
        self.coord_ext = {
            'max_x': 20037508.342789244,
            'min_x': -20037508.342789244,
            'max_y': 20037508.342789244,
            'min_y': -20037508.342789244
        }

        # Set the scene to match world extents
        self.scene.setSceneRect(
            self.coord_ext['min_x'],
            self.coord_ext['min_y'],
            self.coord_ext['max_x'],
            self.coord_ext['max_y']
        )

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)

        # Fit entire map into view
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scene_rect()

    def update_scene_rect(self):
        """Update coordinate extents and scene rect based on the viewport size."""
        self.window_ext = {
            'width': self.viewport().width(),
            'height': self.viewport().height()
        }

        self.set_y_ext()

        # Set a rect centered at (0,0) with width and height proportional to Web Mercator extents
        width = self.coord_ext['max_x'] - self.coord_ext['min_x']
        height = self.coord_ext['max_y'] - self.coord_ext['min_y']
        self.scene.setSceneRect(
            self.coord_ext['min_x'], self.coord_ext['min_y'], width, height
        )

    def set_y_ext(self):
        x_tot = self.coord_ext['max_x'] - self.coord_ext['min_x']
        y_tot = x_tot * self.window_ext['height'] / self.window_ext['width']
        self.coord_ext['max_y'] = y_tot / 2
        self.coord_ext['min_y'] = - y_tot / 2

    

    def mouseMoveEvent(self, event):
        point = self.mapToScene(event.pos())
        lat, lon = mercator_to_latlon(point.x(), point.y())
        self.status_label.setText(f"Lat: {point.y():.2f}, Lon: {point.x():.2f}")
        super().mouseMoveEvent(event)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Viewer")
        self.resize(800, 600)

        self.scene = QGraphicsScene(self)
        self.status_label = QLabel("X: , Y: ")
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
