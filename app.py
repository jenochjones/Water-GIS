import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QToolBar, QPushButton, QDockWidget, QVBoxLayout, QWidget,
    QDialogButtonBox, QLineEdit, QLabel, QDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from wms import get_wms_tiles
#from PIL.Image import ImageQt
from PIL import Image
import ImageQt

class PannableZoomableView(QGraphicsView):
    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.zoom_factor = 1.15
        self.main_window = main_window  # Reference to the main window

        # Initialize map-related properties
        self.scene = scene
        self.current_zoom = 2  # Default zoom level
        self.update_map()

    def update_map(self):
        # Calculate the bounding box in lat/lon based on the scene rect
        scene_rect = self.scene.sceneRect()
        top_left = self.mapToScene(scene_rect.topLeft().toPoint())
        bottom_right = self.mapToScene(scene_rect.bottomRight().toPoint())

        lat_min = min(top_left.y(), bottom_right.y())
        lat_max = max(top_left.y(), bottom_right.y())
        lon_min = min(top_left.x(), bottom_right.x())
        lon_max = max(top_left.x(), bottom_right.x())

        # Fetch WMS tiles using the bounding box
        tiles = get_wms_tiles(lat_min, lon_min, lat_max, lon_max)
        self.scene.clear()

        # Display the tiles in the scene
        tile_size = 256  # Pixels per tile
        for row_idx, row in enumerate(tiles):
            for col_idx, tile in enumerate(row):
                qt_image = ImageQt(tile)
                pixmap = QPixmap.fromImage(qt_image)
                x_pos = col_idx * tile_size
                y_pos = row_idx * tile_size
                self.scene.addPixmap(pixmap).setPos(x_pos, y_pos)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.current_zoom = min(self.current_zoom + 1, 18)  # Limit max zoom
        else:
            self.current_zoom = max(self.current_zoom - 1, 1)  # Limit min zoom

        self.update_map()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update_map()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Viewer")
        self.resize(800, 600)

        # Create the scene and view
        scene = QGraphicsScene(self)
        scene.setSceneRect(-180, -90, 360, 180)  # Approximate world bounds in lat/lon
        view = PannableZoomableView(scene, self)

        self.setCentralWidget(view)

        # Create toolbars and buttons
        self.create_toolbars()

    def create_toolbars(self):
        # File toolbar
        file_toolbar = QToolBar("File Toolbar", self)
        self.addToolBar(file_toolbar)

        new_file_btn = QPushButton(QIcon("icons/new_proj.png"), "", self)
        new_file_btn.setIconSize(QSize(35, 35))
        new_file_btn.setShortcut("Ctrl+N")
        file_toolbar.addWidget(new_file_btn)

        open_btn = QPushButton(QIcon("icons/open.png"), "", self)
        open_btn.setShortcut("Ctrl+O")
        open_btn.setIconSize(QSize(35, 35))
        file_toolbar.addWidget(open_btn)

        save_btn = QPushButton(QIcon("icons/save.png"), "", self)
        save_btn.setShortcut("Ctrl+S")
        save_btn.setIconSize(QSize(35, 35))
        file_toolbar.addWidget(save_btn)

        # Run toolbar
        run_toolbar = QToolBar("Run Toolbar", self)
        self.addToolBar(run_toolbar)

        set_crs_btn = QPushButton(QIcon("icons/crs.png"), "", self)
        set_crs_btn.setIconSize(QSize(35, 35))
        run_toolbar.addWidget(set_crs_btn)

        run_model_btn = QPushButton(QIcon("icons/run.png"), "", self)
        run_model_btn.setShortcut("Ctrl+R")
        run_model_btn.setIconSize(QSize(35, 35))
        run_toolbar.addWidget(run_model_btn)

        # Analysis toolbar
        analysis_toolbar = QToolBar("Analysis Toolbar", self)
        self.addToolBar(analysis_toolbar)

        graph_btn = QPushButton(QIcon("icons/graph.png"), "", self)
        graph_btn.setIconSize(QSize(35, 35))
        analysis_toolbar.addWidget(graph_btn)

        # Draw toolbar
        draw_toolbar = QToolBar("Draw Toolbar", self)
        self.addToolBar(draw_toolbar)

        select_btn = QPushButton(QIcon("icons/select.png"), "", self)
        select_btn.setIconSize(QSize(35, 35))
        draw_toolbar.addWidget(select_btn)

        add_node_btn = QPushButton(QIcon("icons/add_node.png"), "", self)
        add_node_btn.setIconSize(QSize(35, 35))
        draw_toolbar.addWidget(add_node_btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
