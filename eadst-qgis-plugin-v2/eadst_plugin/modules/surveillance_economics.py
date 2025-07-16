# Placeholder for surveillance_economics module
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout
class SurveillanceEconomicsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("surveillance economics".title())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Functionality for surveillance economics to be implemented here."))


# eadst_plugin/modules/surveillance_economics.py

import json
from qgis.PyQt.QtWidgets import (QDialog, QWizard, QWizardPage, QVBoxLayout, QFormLayout, 
                                 QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QFileDialog, 
                                 QDoubleSpinBox, QTableWidget, QTableWidgetItem, 
                                 QHeaderView, QPushButton, QTabWidget, QWidget)
from qgis.core import Qgis, QgsProject
from .utils import show_message, get_economic_parameters, save_economic_parameters

# --- Helper Class for Wizard Pages ---
class WizardPage(QWizardPage):
    """A standardized page for the Surveillance Designer Wizard."""
    def __init__(self, title, subtitle, prompts, parent=None):
        super(WizardPage, self).__init__(parent)
        self.setTitle(title)
        self.setSubTitle(subtitle)
        layout = QFormLayout()
        for field_name, prompt_text in prompts:
            widget = QTextEdit()
            self.registerField(f"{field_name}*", widget, "plainText")
            layout.addRow(QLabel(prompt_text), widget)
        self.setLayout(layout)

# --- Main Tools ---
class SurveillanceDesigner(QWizard):
    """A wizard to create a surveillance scheme based on the USDA 9-element guide."""
    def __init__(self, iface, parent=None):
        super(SurveillanceDesigner, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Surveillance Scheme Designer")
        self.setMinimumSize(800, 600)
        
        # Create and add each of the 9 pages based on the USDA guide
        prompts = [
            ("objective", "1. Surveillance Objective:"), ("context", "2. Surveillance Context:"),
            ("inference_group", "3. Inference Group:"), ("unit_selection", "4. Unit Selection:"),
            ("measurements", "5. Measurements:"), ("tools", "6. Measurement Tools:"),
            ("number_units", "7. Number of Units:"), ("frequency", "8. Frequency & Duration:"),
            ("data_recording", "9. Data Recording:")
        ]
        page = WizardPage("Surveillance Scheme Details", "Complete all 9 elements for the surveillance plan.", prompts)
        self.addPage(page)

    def accept(self):
        """Saves the collected wizard data to a JSON file."""
        scheme_data = {field.replace('*',''): self.field(field) for field in self.fieldNames()}
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Surveillance Scheme", "", "EADST Scheme Files (*.eadss.json)")
        if filePath:
            try:
                with open(filePath, 'w') as f:
                    json.dump(scheme_data, f, indent=4)
                show_message(self.iface, f"Scheme saved to {filePath}", level=Qgis.Success)
            except Exception as e:
                show_message(self.iface, f"Failed to save scheme file: {e}", level=Qgis.Critical)
        super(SurveillanceDesigner, self).accept()

class SURVCosTDialog(QDialog):
    """Dialog to calculate the cost of a surveillance scheme."""
    def __init__(self, iface, parent=None):
        super(SURVCosTDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("SURVCosT - Surveillance Program Costing")
        self.setMinimumSize(500, 300)

        self.load_button = QPushButton("Load Surveillance Scheme (.eadss.json)...")
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Cost Component", "Estimated Cost (USD)"])

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.result_table)
        self.setLayout(layout)

        self.load_button.clicked.connect(self.calculate_cost)

    def calculate_cost(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Surveillance Scheme", "", "EADST Scheme Files (*.eadss.json)")
        if not filePath: return
        
        try:
            with open(filePath, 'r') as f:
                scheme_data = json.load(f)
            
            # This is a mock calculation. A real implementation would parse the scheme_data
            # to get sample sizes, duration, etc.
            params = get_economic_parameters()
            personnel_cost = 10 * params.get('staff_daily_rate', 40.0) # 10 staff days
            logistics_cost = 500 * params.get('cost_per_km', 0.50) # 500 km travel
            lab_cost = 200 * params.get('cost_elisa_test', 5.0) # 200 ELISA tests
            total_cost = personnel_cost + logistics_cost + lab_cost

            self.result_table.setRowCount(4)
            self.result_table.setItem(0, 0, QTableWidgetItem("Personnel Costs"))
            self.result_table.setItem(0, 1, QTableWidgetItem(f"{personnel_cost:,.2f}"))
            self.result_table.setItem(1, 0, QTableWidgetItem("Logistics Costs"))
            self.result_table.setItem(1, 1, QTableWidgetItem(f"{logistics_cost:,.2f}"))
            self.result_table.setItem(2, 0, QTableWidgetItem("Laboratory Costs"))
            self.result_table.setItem(2, 1, QTableWidgetItem(f"{lab_cost:,.2f}"))
            self.result_table.setItem(3, 0, QTableWidgetItem("Total Estimated Cost"))
            self.result_table.setItem(3, 1, QTableWidgetItem(f"{total_cost:,.2f}"))
            self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
            show_message(self.iface, f"Could not process scheme file: {e}", level=Qgis.Critical)

class OutCosTDialog(QDialog):
    # ... (Implementation as defined in previous response) ...
    # This remains a good placeholder structure.
    pass

class EconomicParametersDialog(QDialog):
    """Dialog for editing and viewing economic parameters stored in the database."""
    def __init__(self, iface, parent=None):
        super(EconomicParametersDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Economic Parameter Database")
        
        self.params = get_economic_parameters()
        self.widgets = {}
        
        layout = QFormLayout()
        for key, value in sorted(self.params.items()):
            label = QLabel(f"{key.replace('_', ' ').title()}:")
            spin_box = QDoubleSpinBox()
            spin_box.setDecimals(2)
            spin_box.setMaximum(1e12)
            spin_box.setValue(value)
            self.widgets[key] = spin_box
            layout.addRow(label, spin_box)
            
        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.save_parameters)
        buttonBox.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttonBox)
        self.setLayout(main_layout)

    def save_parameters(self):
        updated_params = {key: widget.value() for key, widget in self.widgets.items()}
        if save_economic_parameters(updated_params):
            show_message(self.iface, "Economic parameters saved successfully.", level=Qgis.Success)
            self.accept()
        else:
            show_message(self.iface, "Failed to save parameters to database.", level=Qgis.Critical)