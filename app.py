import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QToolBar, QPushButton, QDockWidget, QVBoxLayout, QWidget,
    QDialogButtonBox, QLineEdit, QLabel, QDialog, QSpacerItem, QSizePolicy
)

from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPen, QPainter, QIcon

from map import is_valid_epsg


class EPSGPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Coordinate Reference System")

        # Create layout and widgets
        layout = QVBoxLayout(self)
        label = QLabel("EPSG Code:")
        self.text_input = QLineEdit(self)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        
        # Add widgets to layout
        layout.addWidget(label)
        layout.addWidget(self.text_input)
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)


class PannableZoomableView(QGraphicsView):
    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.zoom_factor = 1.15
        self.main_window = main_window  # Reference to the main window for status bar updates

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(self.zoom_factor, self.zoom_factor)
        else:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Get the scene coordinates of the mouse click
            scene_pos = self.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()

            # Update the status bar with the coordinates
            self.main_window.statusBar().showMessage(f"Clicked at: x = {x:.2f}, y = {y:.2f}")

        # Call the parent class's method to retain default behavior
        super().mousePressEvent(event)


class CartesianGridScene(QGraphicsScene):
    def __init__(self, rect):
        super().__init__(rect)

    def drawBackground(self, painter, rect):
        # Draw Cartesian grid
        grid_pen = QPen(Qt.lightGray)
        grid_pen.setWidth(0)
        painter.setPen(grid_pen)

        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        # Draw vertical grid lines
        for x in range(left - (left % 10), right, 10):
            painter.drawLine(x, top, x, bottom)

        # Draw horizontal grid lines
        for y in range(top - (top % 10), bottom, 10):
            painter.drawLine(left, y, right, y)

        # Draw axes
        axis_pen = QPen(Qt.black)
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)
        painter.drawLine(0, int(rect.top()), 0, int(rect.bottom()))  # y-axis
        painter.drawLine(int(rect.left()), 0, int(rect.right()), 0)  # x-axis


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.crs = None

        # Define the scene's bounding rectangle
        scene_rect = QRectF(-500, -500, 1000, 1000)

        # Create the scene and view
        scene = CartesianGridScene(scene_rect)
        view = PannableZoomableView(scene, self)

        self.setCentralWidget(view)
        self.setWindowTitle("WATER-GIS")
        self.resize(800, 600)

        # Create a file toolbar
        top_file_toolbar = QToolBar("File Toolbar", self)
        self.addToolBar(top_file_toolbar)

        # New Project Button
        new_file_btn = QPushButton(QIcon("icons/new_proj.png"), "", self)
        new_file_btn.setIconSize(QSize(35, 35))
        new_file_btn.setShortcut("Ctrl+N")
        top_file_toolbar.addWidget(new_file_btn)

        # Open File Button
        open_btn = QPushButton(QIcon("icons/open.png"), "", self)
        open_btn.setShortcut("Ctrl+O")
        open_btn.setIconSize(QSize(35, 35))
        top_file_toolbar.addWidget(open_btn)

        # Save Project Button
        save_btn = QPushButton(QIcon("icons/save.png"), "", self)
        save_btn.setShortcut("Ctrl+S")
        save_btn.setIconSize(QSize(35, 35))
        top_file_toolbar.addWidget(save_btn)

        # Create a run toolbar
        top_run_toolbar = QToolBar("Run Toolbar", self)
        self.addToolBar(top_run_toolbar)

        # Set CRS Button
        set_crs_btn = QPushButton(QIcon("icons/crs.png"), "", self)
        set_crs_btn.setIconSize(QSize(35, 35))
        set_crs_btn.clicked.connect(self.open_epsg_popup)
        top_run_toolbar.addWidget(set_crs_btn)

        # Run Model Button
        run_model_btn = QPushButton(QIcon("icons/run.png"), "", self)
        run_model_btn.setShortcut("Ctrl+R")
        run_model_btn.setIconSize(QSize(35, 35))
        top_run_toolbar.addWidget(run_model_btn)

        # Create analysis toolbar
        top_analysis_toolbar = QToolBar("Analysis Toolbar", self)
        self.addToolBar(top_analysis_toolbar)

        # Graph Results Button
        graph_btn = QPushButton(QIcon("icons/graph.png"), "", self)
        graph_btn.setIconSize(QSize(35, 35))
        top_analysis_toolbar.addWidget(graph_btn)

        # Create a draw toolbar
        top_draw_toolbar = QToolBar("Draw Toolbar", self)
        self.addToolBar(top_draw_toolbar)

        # Select Button
        select_btn = QPushButton(QIcon("icons/select.png"), "", self)
        select_btn.setIconSize(QSize(35, 35))
        top_draw_toolbar.addWidget(select_btn)

        # Add Node Button
        add_node_btn = QPushButton(QIcon("icons/add_node.png"), "", self)
        add_node_btn.setIconSize(QSize(35, 35))
        top_draw_toolbar.addWidget(add_node_btn)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Dock widget for tools
        self.tools_dock = QDockWidget("Model Explorer", self)
        self.tools_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        tools_layout = QVBoxLayout()

        # Add a label for CRS at the bottom of the layout
        self.crs_label = QLabel("CRS: None")
        self.crs_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        # Add a spacer to push the label to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        tools_layout.addItem(spacer)
        tools_layout.addWidget(self.crs_label)

        tools_container = QWidget()
        tools_container.setLayout(tools_layout)
        self.tools_dock.setWidget(tools_container)
        self.tools_dock.setMinimumWidth(150)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tools_dock)

        # Set the style to match EPANET
        self.setStyleSheet(self.waterGIS_style())

    def open_epsg_popup(self):
        # Create and show the popup dialog
        popup = EPSGPopup(self)
        if popup.exec_() == QDialog.Accepted:
            epsg_code = popup.text_input.text()
            if is_valid_epsg(epsg_code):
                self.crs = epsg_code
                self.crs_label.setText(f"CRS: {epsg_code}")
                self.statusBar().showMessage(f"CRS updated to EPSG:{epsg_code}")
            else:
                self.statusBar().showMessage("EPSG Code is not valid.")
        else:
            self.statusBar().showMessage("CRS Canceled.")

    def waterGIS_style(self):
        return (
            "QMainWindow { background-color: #f0f0f0; color: white; }"
            "QMenuBar { background-color: #e0e0e0; border: 1px solid #a0a0a0; }"
            "QMenu { background-color: #ffffff; border: 1px solid #a0a0a0; }"
            "QToolBar { background-color: #d0d0d0; border: 1px solid #a0a0a0; }"
            "QStatusBar { background-color: #e0e0e0; border: 1px solid #a0a0a0; color: black; }"
            "QDockWidget { background-color: #ffffff; border: 1px solid #a0a0a0; color: black; }"
            "QTreeWidget { background-color: #ffffff; border: 1px solid #a0a0a0; }"
            "QPushButton { padding: 0; background: transparent; }"
            "QPushButton:hover { background-color: #d0d0d0; }"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
