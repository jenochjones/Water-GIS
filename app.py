import sys
import io
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDockWidget,
    QVBoxLayout, QWidget, QGraphicsView, QToolBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

from file_toolbar import (create_new_project, load_inp_file)
from map import initialize_map


class WaterGIS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.saved = False
        self.model_gis = {}
        self.project = None

        self.crs = None
        
        self.pipes = None
        self.junctions = None
        self.tanks = None
        self.valves = None
        self.reservoirs = None

    def init_ui(self):
        self.setWindowTitle("WATER-GIS")
        self.setGeometry(100, 100, 1200, 800)

        # Create a file toolbar
        top_file_toolbar = QToolBar("File Toolbar", self)
        self.addToolBar(top_file_toolbar)

        # New Project Button
        new_file_btn = QPushButton(QIcon("icons/new_proj.png"), "", self)
        new_file_btn.setIconSize(QSize(35, 35))
        new_file_btn.setShortcut("Ctrl+N")
        new_file_btn.clicked.connect(lambda: create_new_project(self))
        top_file_toolbar.addWidget(new_file_btn)

        # Open File Button
        open_btn = QPushButton(QIcon("icons/open.png"), "", self)
        open_btn.setShortcut("Ctrl+O")
        open_btn.setIconSize(QSize(35, 35))
        open_btn.clicked.connect(lambda: load_inp_file(self))
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

        # Status bar
        self.statusBar().showMessage("Ready")

        # Central widget (map area)
        self.map_view = QWebEngineView()
        self.setCentralWidget(self.map_view)

        # Dock widget for tools
        self.tools_dock = QDockWidget("Model Explorer", self)
        self.tools_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        tools_layout = QVBoxLayout()

        tools_container = QWidget()
        tools_container.setLayout(tools_layout)
        self.tools_dock.setWidget(tools_container)
        self.tools_dock.setMinimumWidth(150)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tools_dock)

        # Set the style to match EPANET
        self.setStyleSheet(self.waterGIS_style())


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
            "QPushButton:hover { background-color: #d0d0d0 }"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaterGIS()
    window.show()
    sys.exit(app.exec_())
