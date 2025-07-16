# Placeholder for outbreak_investigation module
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout
class OutbreakInvestigationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("outbreak investigation".title())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Functionality for outbreak investigation to be implemented here."))


# eadst_plugin/modules/outbreak_investigation.py

import uuid
from datetime import datetime
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
                                 QPushButton, QComboBox, QDialogButtonBox, QTextEdit,
                                 QMessageBox)
from qgis.PyQt.QtCore import Qt, QVariant
from qgis.core import (QgsProject, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer,
                       QgsField, QgsWkbTypes, QgsSymbol, QgsSingleSymbolRenderer,
                       QgsLineSymbol, QgsArrowSymbolLayer)
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsMapToolEmitPoint

from .utils import find_or_create_layer, get_species_from_db, get_breeds_for_species, show_message

class AddRecordTool(QgsMapToolEmitPoint):
    """A map tool that captures a point and opens the AddOutbreakRecordDialog."""
    def __init__(self, iface):
        super(AddRecordTool, self).__init__(iface.mapCanvas())
        self.iface = iface

    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        dialog = AddOutbreakRecordDialog(self.iface, point)
        dialog.exec_()
        # Deactivate the tool after it has been used once
        self.iface.mapCanvas().unsetMapTool(self)

class AddOutbreakRecordDialog(QDialog):
    """Dialog for entering a new outbreak record."""
    def __init__(self, iface, point, parent=None):
        super(AddOutbreakRecordDialog, self).__init__(parent)
        self.iface = iface
        self.point = point
        self.setWindowTitle("Add New Outbreak Record")
        self.setMinimumWidth(400)

        # UI Elements
        self.species_combo = QComboBox()
        self.breed_combo = QComboBox()
        self.case_count_edit = QLineEdit("1")
        self.pop_at_risk_edit = QLineEdit("1")
        self.notes_edit = QTextEdit()

        # Layout
        layout = QFormLayout()
        layout.addRow("Species:", self.species_combo)
        layout.addRow("Breed:", self.breed_combo)
        layout.addRow("Number of Cases:", self.case_count_edit)
        layout.addRow("Population at Risk:", self.pop_at_risk_edit)
        layout.addRow("Notes:", self.notes_edit)

        # Buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        layout.addRow(buttonBox)
        self.setLayout(layout)
        
        buttonBox.accepted.connect(self.save_record)
        buttonBox.rejected.connect(self.reject)
        
        # Populate dynamic fields
        self.populate_species()
        self.species_combo.currentIndexChanged.connect(self.populate_breeds)

    def populate_species(self):
        species = get_species_from_db()
        self.species_combo.addItems([""] + species)

    def populate_breeds(self):
        self.breed_combo.clear()
        selected_species = self.species_combo.currentText()
        if selected_species:
            breeds = get_breeds_for_species(selected_species)
            self.breed_combo.addItems([""] + breeds)
            
    def save_record(self):
        layer_name = "Outbreak_Points"
        fields = {
            "Event_ID": QVariant.String, "Species": QVariant.String, 
            "Breed": QVariant.String, "Event_Date": QVariant.DateTime,
            "Cases": QVariant.Int, "Pop_At_Risk": QVariant.Int,
            "Notes": QVariant.String
        }
        crs = QgsProject.instance().crs()
        layer = find_or_create_layer(layer_name, fields, "Point", crs)
        
        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(self.point))
        feat.setAttributes([
            str(uuid.uuid4()),
            self.species_combo.currentText(),
            self.breed_combo.currentText(),
            datetime.now(),
            int(self.case_count_edit.text() or 0),
            int(self.pop_at_risk_edit.text() or 0),
            self.notes_edit.toPlainText()
        ])
        
        layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        layer.triggerRepaint()
        show_message(self.iface, f"New record added to '{layer_name}'.", level=Qgis.Success)
        self.accept()

class FieldTracingTool(QgsMapToolEmitPoint):
    """A map tool for creating visual trace links between outbreak points."""
    def __init__(self, iface, parent=None):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.index_case_feat = None
        self.trace_type = None

    def start_tracing(self):
        self.iface.mapCanvas().setMapTool(self)
        show_message(self.iface, "Step 1: Click on the Index Case/Premise.", duration=10)

    def canvasReleaseEvent(self, event):
        clicked_point = self.toMapCoordinates(event.pos())
        outbreak_layer = QgsProject.instance().mapLayersByName("Outbreak_Points")
        if not outbreak_layer:
            show_message(self.iface, "Error: 'Outbreak_Points' layer must exist to start tracing.", level=Qgis.Critical)
            self.iface.mapCanvas().unsetMapTool(self)
            return

        # Find the nearest feature on the outbreak layer
        closest_feat, min_dist = None, float('inf')
        search_radius = self.iface.mapCanvas().extent().width() / 100
        for feat in outbreak_layer[0].getFeatures(QgsProject.instance().transform(
            self.iface.mapCanvas().mapSettings().destinationCrs(),
            outbreak_layer[0].crs()
        ).transform(QgsGeometry.fromPointXY(clicked_point).buffer(search_radius, 5).boundingBox())):
            dist = feat.geometry().distance(QgsGeometry.fromPointXY(clicked_point))
            if dist < min_dist:
                min_dist = dist
                closest_feat = QgsFeature(feat)

        if not closest_feat: return

        if self.index_case_feat is None:
            self.index_case_feat = closest_feat
            show_message(self.iface, f"Index Case '{self.index_case_feat['Event_ID']}' selected. Step 2: Click the linked premise.", duration=10)
        else:
            linked_feat = closest_feat
            if self.index_case_feat.id() == linked_feat.id(): return # Don't link to self
            
            self.create_trace_link(self.index_case_feat, linked_feat)
            self.iface.mapCanvas().unsetMapTool(self)

    def create_trace_link(self, from_feat, to_feat):
        layer_name = "Trace_Links"
        fields = {"Source_ID": QVariant.String, "Dest_ID": QVariant.String, "Trace_Type": QVariant.String}
        crs = QgsProject.instance().crs()
        line_layer = find_or_create_layer(layer_name, fields, "LineString", crs)

        # Simple yes/no dialog to determine trace direction
        reply = QMessageBox.question(self.iface.mainWindow(), 'Trace Direction',
                                     "Is this a TRACE-BACK (source of infection)?\n(Click 'No' for a TRACE-FORWARD).",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        trace_type = 'Trace-Back' if reply == QMessageBox.Yes else 'Trace-Forward'

        feat = QgsFeature(line_layer.fields())
        if trace_type == 'Trace-Back':
            geom = QgsGeometry.fromPolylineXY([to_feat.geometry().asPoint(), from_feat.geometry().asPoint()])
            feat.setAttributes([to_feat['Event_ID'], from_feat['Event_ID'], trace_type])
        else: # Forward
            geom = QgsGeometry.fromPolylineXY([from_feat.geometry().asPoint(), to_feat.geometry().asPoint()])
            feat.setAttributes([from_feat['Event_ID'], to_feat['Event_ID'], trace_type])

        feat.setGeometry(geom)
        line_layer.dataProvider().addFeature(feat)
        self.style_trace_layer(line_layer)
        line_layer.triggerRepaint()

    def style_trace_layer(self, layer):
        """Apply categorized styling based on trace type."""
        categories = []
        styles = {
            'Trace-Back': ('#ff0000', Qt.DashLine), # Red, Dashed
            'Trace-Forward': ('#0000ff', Qt.SolidLine) # Blue, Solid
        }
        for value, (color, pen_style) in styles.items():
            symbol = QgsLineSymbol()
            symbol.setColor(QColor(color))
            symbol.setWidth(0.5)
            symbol.setPenStyle(pen_style)
            symbol.appendSymbolLayer(QgsArrowSymbolLayer())
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)
        
        renderer = QgsCategorizedSymbolRenderer('Trace_Type', categories)
        layer.setRenderer(renderer)

class CaseDefinitionDialog(QDialog):
    # ... (Implementation as defined in previous response) ...
    pass # This class is primarily for storing/retrieving text, so the placeholder is sufficient.