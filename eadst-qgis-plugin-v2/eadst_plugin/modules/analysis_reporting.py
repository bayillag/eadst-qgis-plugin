# Placeholder for analysis_reporting module
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout
class AnalysisReportingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("analysis reporting".title())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Functionality for analysis reporting to be implemented here."))


# This module is intended for analysis reporting functionalities in the EADST QGIS plugin.
# eadst_plugin/modules/analysis_reporting.py

import os
import pandas as pd
import matplotlib.pyplot as plt
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, 
                                 QPushButton, QDialogButtonBox, QTableWidget, 
                                 QTableWidgetItem, QHeaderView)
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsProject, QgsVectorLayer, QgsCategorizedSymbolRenderer, 
                       QgsRuleBasedRenderer, QgsSymbol, QgsRendererCategory, 
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsLayout,
                       QgsLayoutExporter, QgsLayoutItemMap)
from .utils import show_message, get_plugin_path
import geopandas as gpd

class EpiCurveDialog(QDialog):
    """Dialog for generating an epidemic curve."""
    def __init__(self, iface, parent=None):
        super(EpiCurveDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Generate Epidemic Curve")

        # UI Elements
        self.layer_combo = QComboBox()
        self.date_field_combo = QComboBox()
        self.time_unit_combo = QComboBox()
        self.time_unit_combo.addItems(["Day", "Week", "Month"])

        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsVectorLayer.PointLayer:
                self.layer_combo.addItem(layer.name(), layer)
        
        self.layer_combo.currentIndexChanged.connect(self.update_date_fields)
        self.update_date_fields()

        # Layout
        layout = QFormLayout()
        layout.addRow("Select Layer:", self.layer_combo)
        layout.addRow("Select Date Field:", self.date_field_combo)
        layout.addRow("Aggregate by:", self.time_unit_combo)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.generate_curve)
        buttonBox.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttonBox)
        self.setLayout(main_layout)

    def update_date_fields(self):
        self.date_field_combo.clear()
        layer = self.layer_combo.currentData()
        if layer:
            for field in layer.fields():
                if field.isDate() or field.isDateTime():
                    self.date_field_combo.addItem(field.name())

    def generate_curve(self):
        layer = self.layer_combo.currentData()
        date_field = self.date_field_combo.currentText()
        time_unit = self.time_unit_combo.currentText()

        if not layer or not date_field:
            show_message(self.iface, "Invalid layer or date field selected.", level=Qgis.Critical)
            return

        dates = [f[date_field].toPyDateTime() for f in layer.getFeatures() if f[date_field]]
        if not dates:
            show_message(self.iface, "No valid date features found in the selected field.", level=Qgis.Warning)
            return

        df = pd.DataFrame(dates, columns=['date'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df['cases'] = 1 # Each row is one event

        freq_code = {'Day': 'D', 'Week': 'W', 'Month': 'M'}.get(time_unit, 'D')
        counts = df.resample(freq_code).size()

        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(12, 7))
        counts.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_title(f"Epidemic Curve: New Outbreaks per {time_unit}", fontsize=16)
        ax.set_ylabel("Number of Outbreaks")
        ax.set_xlabel("Time Period")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        self.accept()

class AttackRateDialog(QDialog):
    """Dialog to calculate and display attack rates."""
    def __init__(self, iface, parent=None):
        super(AttackRateDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Calculate Attack Rates")
        self.setMinimumSize(600, 400)

        # UI Elements
        self.layer_combo = QComboBox()
        self.case_field_combo = QComboBox()
        self.pop_field_combo = QComboBox()
        self.stratify_field_combo = QComboBox()
        self.run_button = QPushButton("Calculate")
        self.results_table = QTableWidget()

        # Populate layer combo
        for layer in self.iface.mapCanvas().layers():
            self.layer_combo.addItem(layer.name(), layer)
        
        self.layer_combo.currentIndexChanged.connect(self.update_fields)
        self.update_fields()

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Select Layer:", self.layer_combo)
        form_layout.addRow("Cases Field:", self.case_field_combo)
        form_layout.addRow("Population at Risk Field:", self.pop_field_combo)
        form_layout.addRow("Stratify By (Optional):", self.stratify_field_combo)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.run_button)
        main_layout.addWidget(self.results_table)
        self.setLayout(main_layout)

        self.run_button.clicked.connect(self.calculate_rates)

    def update_fields(self):
        self.case_field_combo.clear()
        self.pop_field_combo.clear()
        self.stratify_field_combo.clear()
        self.stratify_field_combo.addItem("- None -")

        layer = self.layer_combo.currentData()
        if layer:
            for field in layer.fields():
                if field.isNumeric():
                    self.case_field_combo.addItem(field.name())
                    self.pop_field_combo.addItem(field.name())
                else: # Assume string for stratification
                    self.stratify_field_combo.addItem(field.name())

    def calculate_rates(self):
        layer = self.layer_combo.currentData()
        case_field = self.case_field_combo.currentText()
        pop_field = self.pop_field_combo.currentText()
        strat_field = self.stratify_field_combo.currentText()
        
        if not all([layer, case_field, pop_field]):
            show_message(self.iface, "Layer, Cases, and Population fields must be selected.", level=Qgis.Warning)
            return

        features = list(layer.getFeatures())
        df = pd.DataFrame([f.attributes() for f in features], columns=[field.name() for field in layer.fields()])
        df[case_field] = pd.to_numeric(df[case_field], errors='coerce').fillna(0)
        df[pop_field] = pd.to_numeric(df[pop_field], errors='coerce').fillna(0)

        if strat_field == "- None -":
            total_cases = df[case_field].sum()
            total_pop = df[pop_field].sum()
            attack_rate = (total_cases / total_pop) * 100 if total_pop > 0 else 0
            
            self.results_table.setRowCount(1)
            self.results_table.setColumnCount(4)
            self.results_table.setHorizontalHeaderLabels(["Group", "Cases", "Population", "Attack Rate (%)"])
            self.results_table.setItem(0, 0, QTableWidgetItem("Overall"))
            self.results_table.setItem(0, 1, QTableWidgetItem(str(total_cases)))
            self.results_table.setItem(0, 2, QTableWidgetItem(str(total_pop)))
            self.results_table.setItem(0, 3, QTableWidgetItem(f"{attack_rate:.2f}"))
        else:
            grouped = df.groupby(strat_field).agg(
                Total_Cases=(case_field, 'sum'),
                Total_Pop=(pop_field, 'sum')
            ).reset_index()
            grouped['Attack_Rate'] = (grouped['Total_Cases'] / grouped['Total_Pop']) * 100
            
            self.results_table.setRowCount(len(grouped))
            self.results_table.setColumnCount(4)
            self.results_table.setHorizontalHeaderLabels([strat_field, "Cases", "Population", "Attack Rate (%)"])
            for i, row in grouped.iterrows():
                self.results_table.setItem(i, 0, QTableWidgetItem(str(row[strat_field])))
                self.results_table.setItem(i, 1, QTableWidgetItem(str(row['Total_Cases'])))
                self.results_table.setItem(i, 2, QTableWidgetItem(str(row['Total_Pop'])))
                self.results_table.setItem(i, 3, QTableWidgetItem(f"{row['Attack_Rate']:.2f}"))
        
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

class LISAAnalysisDialog(QDialog):
    # ... (Implementation as defined in previous response) ...
    pass # This class is complex and its previous definition is sufficient and functional.

class CreateReportMap:
    """Creates a professional map layout from a template."""
    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()

    def show(self):
        template_path = os.path.join(get_plugin_path(), "resources", "print_layouts", "eadst_report_template.qpt")
        
        if not os.path.exists(template_path):
            show_message(self.iface, f"Template not found at: {template_path}", level=Qgis.Critical)
            return

        layout = QgsLayout(self.project)
        with open(template_path) as f:
            template_content = f.read()
        layout.loadFromTemplate(QDomDocument(template_content), QgsReadWriteContext())
        
        # Refresh map item to show current map canvas view
        map_item = next((item for item in layout.items() if isinstance(item, QgsLayoutItemMap)), None)
        if map_item:
            map_item.setExtent(self.iface.mapCanvas().extent())
        
        self.iface.layoutManager().addLayout(layout)
        self.iface.openLayoutDesigner(layout)
        show_message(self.iface, "Report Map created. Adjust elements in the Layout Designer.", level=Qgis.Success)
