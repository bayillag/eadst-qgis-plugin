# Placeholder for utils module
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout
class UtilsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("utils".title())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Functionality for utils to be implemented here."))

# eadst_plugin/modules/utils.py

import os
import sqlite3
import platform
import subprocess
from qgis.core import Qgis, QgsProject, QgsVectorLayer, QgsField
from PyQt5.QtCore import QVariant

def get_plugin_path():
    """Returns the absolute path to the plugin directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_db_connection():
    """Establishes and returns a connection to the data standard SQLite database."""
    db_path = os.path.join(get_plugin_path(), "resources", "data_standard.db")
    if not os.path.exists(db_path):
        return None
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def find_or_create_layer(layer_name, fields, geometry_type, crs):
    """Finds a layer by name. If not found, creates it with specified fields."""
    project = QgsProject.instance()
    layer = project.mapLayersByName(layer_name)
    if layer:
        return layer[0]
    
    vl = QgsVectorLayer(f"{geometry_type}?crs={crs.authid()}", layer_name, "memory")
    provider = vl.dataProvider()
    
    field_list = [QgsField(name, q_type) for name, q_type in fields.items()]
    provider.addAttributes(field_list)
    vl.updateFields()
    
    project.addMapLayer(vl)
    return vl

def show_message(iface, message, level=Qgis.Info, duration=5):
    """Helper to show a message in the QGIS message bar."""
    iface.messageBar().pushMessage("EADST", message, level=level, duration=duration)

def open_pdf(pdf_name):
    """Opens a PDF from the /docs folder in the default system viewer."""
    docs_path = os.path.join(get_plugin_path(), "docs")
    file_path = os.path.join(docs_path, pdf_name)
    if not os.path.exists(file_path):
        show_message(Qgis.instance().iface(), f"Document not found: {pdf_name}", level=Qgis.Warning)
        return
    try:
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', file_path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(file_path)
        else:                                   # linux variants
            subprocess.call(('xdg-open', file_path))
    except Exception as e:
        show_message(Qgis.instance().iface(), f"Could not open document: {e}", level=Qgis.Critical)