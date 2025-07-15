#!/bin/bash
# Script to create the full directory and file structure for the
# EADST QGIS Plugin v1.0 project.

# Define the root directory name
ROOT_DIR="eadst-qgis-plugin-v1"

# --- Main Script Logic ---
echo "Creating EADST v1.0 QGIS Plugin project structure in ./${ROOT_DIR}/"

# Clean up old directory if it exists
if [ -d "$ROOT_DIR" ]; then
    echo "  -> Removing existing directory..."
    rm -rf "$ROOT_DIR"
fi

mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR" || exit

# --- 1. GitHub Codespace & Development Environment ---
echo "  -> Setting up .devcontainer for GitHub Codespaces..."
mkdir -p .devcontainer
cat > .devcontainer/devcontainer.json << 'EOL'
{
  "name": "EADST v2.0 QGIS Plugin Development",
  "build": { "dockerfile": "Dockerfile", "context": ".." },
  "customizations": {
    "vscode": {
      "settings": { "python.defaultInterpreterPath": "/usr/bin/python3" },
      "extensions": [ "ms-python.python", "ms-toolsai.jupyter" ]
    }
  },
  "postCreateCommand": "pip3 install --no-cache-dir pysal geopandas pandas openpyxl pytest matplotlib",
  "remoteUser": "vscode"
}
EOL
cat > .devcontainer/Dockerfile << 'EOL'
FROM qgis/qgis:latest-build
USER root
RUN useradd -m vscode && apt-get update && apt-get install -y --no-install-recommends python3-pip git && apt-get clean && rm -rf /var/lib/apt/lists/*
USER vscode
EOL

# --- 2. Core Plugin Directory ---
echo "  -> Creating core plugin directory 'eadst_plugin'..."
mkdir -p eadst_plugin/{icons,modules,providers,resources/base_layers,ui}

cat > eadst_plugin/__init__.py << 'EOL'
def classFactory(iface):
    from .main_plugin import EADSTPlugin
    return EADSTPlugin(iface)
EOL

cat > eadst_plugin/main_plugin.py << 'EOL'
import os
from qgis.PyQt.QtWidgets import QAction, QMenu, QMessageBox
from qgis.PyQt.QtGui import QIcon
from .modules.project_setup import ProjectSetupWizard, ImportDataDialog
from .modules.data_management import DataQualityDashboard, AnonymizeDataTool
from .modules.outbreak_investigation import AddRecordTool, FieldTracingTool, CaseDefinitionDialog
from .modules.analysis_reporting import EpiCurveDialog, AttackRateDialog, LISAAnalysisDialog, CreateReportMap
from .modules.surveillance_economics import SurveillanceDesigner, SURVCosTDialog, OutCosTDialog, EconomicParametersDialog
from .modules.training_help import HelpDialog, run_tutorial

class EADSTPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = "&EADST"
        self.toolbar = self.iface.addToolBar("EADST Toolbar")
        self.toolbar.setObjectName("EADSTToolbar")
        self.help_dialog = None

    def initGui(self):
        """Create all menus and toolbar actions."""
        self.eadst_menu = QMenu(self.menu, self.iface.mainWindow().menuBar())
        self.iface.mainWindow().menuBar().insertMenu(self.iface.pluginMenu().actions()[0], self.eadst_menu)

        # Create all submenus
        setup_menu = self.eadst_menu.addMenu("Project Setup")
        data_mgmt_menu = self.eadst_menu.addMenu("Data Management")
        investigation_menu = self.eadst_menu.addMenu("Outbreak Investigation")
        analysis_menu = self.eadst_menu.addMenu("Analysis & Reporting")
        planning_menu = self.eadst_menu.addMenu("Surveillance & Economics")
        training_menu = self.eadst_menu.addMenu("Training & Help")

        # --- Populate Menus ---
        self.add_action(setup_menu, "New Investigation Wizard...", self.run_new_investigation, is_toolbar=True)
        
        self.add_action(data_mgmt_menu, "Import Standardized Data...", self.run_import_data)
        self.add_action(data_mgmt_menu, "Data Quality Dashboard...", self.run_quality_dashboard)
        self.add_action(data_mgmt_menu, "Anonymize Case Data...", self.run_anonymize_data)
        
        self.add_action(investigation_menu, "Add Outbreak Record...", self.run_add_record, is_toolbar=True)
        self.add_action(investigation_menu, "Field Tracing Tool", self.run_field_tracing, is_toolbar=True)
        self.add_action(investigation_menu, "Define Outbreak Case...", self.run_define_case)

        desc_epi_menu = analysis_menu.addMenu("Descriptive Epidemiology")
        self.add_action(desc_epi_menu, "Generate Epidemic Curve...", self.run_epi_curve)
        self.add_action(desc_epi_menu, "Calculate Attack Rates...", self.run_attack_rates)
        
        spatial_analysis_menu = analysis_menu.addMenu("Spatial Pattern Analysis")
        self.add_action(spatial_analysis_menu, "Local Cluster Analysis (LISA)...", self.run_lisa_analysis)
        analysis_menu.addSeparator()
        self.add_action(analysis_menu, "Create Report Map...", self.run_create_report_map)

        self.add_action(planning_menu, "Surveillance Scheme Designer...", self.run_surveillance_designer)
        planning_menu.addSeparator()
        self.add_action(planning_menu, "SURVCosT: Surveillance Costing...", self.run_survcost)
        self.add_action(planning_menu, "OutCosT: Outbreak Impact Costing...", self.run_outcost)
        planning_menu.addSeparator()
        self.add_action(planning_menu, "Edit Economic Parameters...", self.run_edit_eco_params)

        training_help_menu = self.eadst_menu.addMenu("Training & Help")
        tutorial_menu = training_help_menu.addMenu("Interactive Learning Modules")
        self.add_action(tutorial_menu, "Tutorial: Investigating an Outbreak", lambda: run_tutorial(self.iface, "Outbreak Investigation"))
        self.add_action(tutorial_menu, "Tutorial: Designing a Surveillance Scheme", lambda: run_tutorial(self.iface, "Surveillance Design"))
        training_help_menu.addSeparator()
        self.add_action(training_help_menu, "EADST Help & Resources...", self.run_help)
        self.add_action(training_help_menu, "About EADST...", self.show_about)

    def add_action(self, menu, text, callback, is_toolbar=False):
        action = QAction(text, self.iface.mainWindow())
        action.triggered.connect(callback)
        menu.addAction(action)
        if is_toolbar:
            self.toolbar.addAction(action)
        self.actions.append(action)

    def unload(self):
        self.iface.removePluginMenu(self.menu, self.eadst_menu)
        for action in self.actions:
            self.toolbar.removeAction(action)
        del self.toolbar
    
    # --- Callback Functions ---
    def run_new_investigation(self): ProjectSetupWizard(self.iface.mainWindow()).exec_()
    def run_import_data(self): ImportDataDialog(self.iface.mainWindow()).exec_()
    def run_quality_dashboard(self): DataQualityDashboard(self.iface.mainWindow()).exec_()
    def run_anonymize_data(self): AnonymizeDataTool(self.iface.mainWindow()).exec_()
    def run_add_record(self): self.add_record_tool = AddRecordTool(self.iface); self.iface.mapCanvas().setMapTool(self.add_record_tool)
    def run_field_tracing(self): self.field_trace_tool = FieldTracingTool(self.iface); self.field_trace_tool.start_tracing()
    def run_define_case(self): CaseDefinitionDialog(self.iface.mainWindow()).exec_()
    def run_epi_curve(self): EpiCurveDialog(self.iface.mainWindow()).exec_()
    def run_attack_rates(self): AttackRateDialog(self.iface.mainWindow()).exec_()
    def run_lisa_analysis(self): LISAAnalysisDialog(self.iface.mainWindow()).exec_()
    def run_create_report_map(self): CreateReportMap(self.iface).show()
    def run_surveillance_designer(self): SurveillanceDesigner(self.iface.mainWindow()).exec_()
    def run_survcost(self): SURVCosTDialog(self.iface.mainWindow()).exec_()
    def run_outcost(self): OutCosTDialog(self.iface.mainWindow()).exec_()
    def run_edit_eco_params(self): EconomicParametersDialog(self.iface.mainWindow()).exec_()
    def run_help(self):
        if self.help_dialog is None:
            self.help_dialog = HelpDialog(self.iface.mainWindow())
        self.help_dialog.show()
    def show_about(self): QMessageBox.about(self.iface.mainWindow(), "About EADST", "Ethiopian Animal Disease Surveillance Toolbox (EADST) v2.0")
EOL

# metadata.txt
cat > eadst_plugin/metadata.txt << 'EOL'
[general]
name=Ethiopian Animal Disease Surveillance Toolbox
qgisMinimumVersion=3.16
description=A holistic, integrated QGIS plugin for animal health professionals in Ethiopia.
version=1.0.0
author=Bayilla Geda (DVM)
email=bayillag@gmail.com
experimental=True
EOL

# --- Python Module Files ---
echo "  -> Writing Python module scripts..."
touch eadst_plugin/modules/__init__.py
for module in project_setup data_management outbreak_investigation analysis_reporting surveillance_economics training_help utils; do
    echo "Creating eadst_plugin/modules/${module}.py"
    touch "eadst_plugin/modules/${module}.py"
done

# --- providers Directory ---
echo "  -> Writing PySAL provider script..."
mkdir -p eadst_plugin/providers && touch eadst_plugin/providers/__init__.py
cat > eadst_plugin/providers/pysal_provider.py << 'EOL'
# Placeholder for PySAL functions. See previous responses for full code.
def run_lisa_analysis(gdf, attribute_column):
    print(f"PySAL provider called for attribute: {attribute_column}")
    return gdf # Return input for now
EOL

# --- Top-level project files ---
echo "  -> Creating top-level project files..."
touch .gitignore LICENSE README.md

# --- Add Content to Placeholder Files ---
echo "  -> Populating placeholder scripts..."
cat > eadst_plugin/modules/project_setup.py << 'EOL'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
class ProjectSetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Investigation Wizard")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Step-by-step guide to create a new project folder and load base layers."))
class ImportDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Standardized Data")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Wizard to import and validate tabular data against the Ethiopian Data Standard."))
EOL

cat > eadst_plugin/modules/data_management.py << 'EOL'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
class DataQualityDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Quality Dashboard")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Shows completeness and validity metrics for a selected layer."))
class AnonymizeDataTool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anonymize Case Data")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Creates a new layer with randomly displaced point coordinates."))
EOL

cat > eadst_plugin/modules/outbreak_investigation.py << 'EOL'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
from qgis.gui import QgsMapTool
class AddRecordTool(QgsMapTool):
    pass
class FieldTracingTool(QgsMapTool):
    def start_tracing(self): pass
class CaseDefinitionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Define Outbreak Case")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Form to define Animal, Place, Time, and Clinical Criteria for the case."))
EOL

cat > eadst_plugin/modules/analysis_reporting.py << 'EOL'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
class EpiCurveDialog(QDialog): pass
class AttackRateDialog(QDialog): pass
class LISAAnalysisDialog(QDialog): pass
class CreateReportMap:
    def __init__(self, iface): self.iface = iface
    def show(self): self.iface.messageBar().pushMessage("Info", "Opening Print Layout with EADST template...")
EOL

cat > eadst_plugin/modules/surveillance_economics.py << 'EOL'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
class SurveillanceDesigner(QDialog): pass
class SURVCosTDialog(QDialog): pass
class OutCosTDialog(QDialog): pass
class EconomicParametersDialog(QDialog): pass
EOL

cat > eadst_plugin/modules/training_help.py << 'EOL'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
def run_tutorial(iface, tutorial_name):
    iface.messageBar().pushMessage("Info", f"Starting interactive tutorial: {tutorial_name}")
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EADST Help & Resources")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Searchable glossary and data standard browser."))
EOL

# --- Finalization ---
cd ..
echo "---------------------------------------------"
echo "Project structure for '$ROOT_DIR' created successfully."
echo "Remember to:"
echo "  1. Add icon files (.svg) to 'eadst_plugin/icons/'"
echo "  2. Add base layer shapefiles to 'eadst_plugin/resources/base_layers/'"
echo "  3. Create and populate 'eadst_plugin/resources/data_standard.db' using the provided Python script."
echo "  4. Add PDF documents to the 'docs/' folder."
echo "---------------------------------------------"
# End of script
