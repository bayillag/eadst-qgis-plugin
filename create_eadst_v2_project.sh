#!/bin/bash
# Script to create the full directory and file structure for the
# EADST QGIS Plugin v3.0 project.

# Define the root directory name
ROOT_DIR="eadst-qgis-plugin-v3"

# --- Main Script Logic ---
echo "Creating EADST v3.0 QGIS Plugin project structure in ./${ROOT_DIR}/"

# Clean up old directory if it exists
if [ -d "$ROOT_DIR" ]; then
    echo "  -> Removing existing directory..."
    rm -rf "$ROOT_DIR"
fi

mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR" || exit

# --- 1. .devcontainer Directory ---
echo "  -> Setting up .devcontainer for GitHub Codespaces..."
mkdir -p .devcontainer
# devcontainer.json
cat > .devcontainer/devcontainer.json << 'EOL'
{
  "name": "EADST v2.0 QGIS Plugin Development", "build": { "dockerfile": "Dockerfile", "context": ".." },
  "customizations": { "vscode": { "settings": { "python.defaultInterpreterPath": "/usr/bin/python3" }, "extensions": [ "ms-python.python", "ms-toolsai.jupyter" ] } },
  "postCreateCommand": "pip3 install --user --no-cache-dir pysal geopandas pandas openpyxl matplotlib pytest", "remoteUser": "vscode"
}
EOL
# Dockerfile
cat > .devcontainer/Dockerfile << 'EOL'
FROM qgis/qgis:latest
USER root
RUN useradd -m vscode && apt-get update && apt-get install -y --no-install-recommends python3-pip git && apt-get clean && rm -rf /var/lib/apt/lists/*
USER vscode
EOL

# --- 2. eadst_plugin Directory ---
echo "  -> Creating core plugin directory 'eadst_plugin'..."
mkdir -p eadst_plugin/{icons,modules,providers,resources/base_layers,ui}

# __init__.py
cat > eadst_plugin/__init__.py << 'EOL'
def classFactory(iface):
    from .main_plugin import EADSTPlugin
    return EADSTPlugin(iface)
EOL

# main_plugin.py (Using your provided structure)
cat > eadst_plugin/main_plugin.py << 'EOL'
import os
from qgis.PyQt.QtWidgets import QAction, QMenu, QMessageBox
from qgis.PyQt.QtGui import QIcon

# Import all module classes
from .modules.project_setup import ProjectSetupWizard
from .modules.data_management import ImportDataDialog, DataQualityDashboard, AnonymizeDataTool
from .modules.outbreak_investigation import AddRecordTool, FieldTracingTool, CaseDefinitionDialog
from .modules.analysis_reporting import EpiCurveDialog, LISAAnalysisDialog, CreateReportMap
from .modules.one_health_coordination import MCM_OT_Wizard, JRA_OT_Wizard, SIS_OT_Wizard
from .modules.surveillance_economics import SurveillanceDesigner, SURVCosTDialog, OutCosTDialog, EconomicParametersDialog
from .modules.help import HelpDialog
from .modules.training import run_tutorial

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
        """Create all menus and toolbar actions for EADST v2.0."""
        self.eadst_menu = QMenu(self.menu, self.iface.mainWindow().menuBar())
        self.iface.mainWindow().menuBar().insertMenu(self.iface.pluginMenu().actions()[0], self.eadst_menu)

        # Create all top-level menus
        setup_menu = self.eadst_menu.addMenu("Project Setup")
        data_mgmt_menu = self.eadst_menu.addMenu("Data Management")
        investigation_menu = self.eadst_menu.addMenu("Outbreak Investigation")
        analysis_menu = self.eadst_menu.addMenu("Analysis & Reporting")
        one_health_menu = self.eadst_menu.addMenu("One Health Coordination")
        planning_menu = self.eadst_menu.addMenu("Surveillance & Economics")
        training_menu = self.eadst_menu.addMenu("Training")
        help_menu = self.eadst_menu.addMenu("Help")
        
        # --- Populate Menus with Actions ---
        self.add_action(setup_menu, "New Investigation Project...", self.run_new_investigation, 'icons/new_project.svg', is_toolbar=True)
        self.add_action(data_mgmt_menu, "Import Standardized Data...", self.run_import_data, 'icons/import_data.svg')
        self.add_action(data_mgmt_menu, "Data Quality Dashboard...", self.run_quality_dashboard, 'icons/quality_dashboard.svg')
        self.add_action(investigation_menu, "Add Outbreak Record...", self.run_add_record, 'icons/add_record.svg', is_toolbar=True)
        self.add_action(investigation_menu, "Field Tracing Tool", self.run_field_tracing, 'icons/field_tracing.svg', is_toolbar=True)
        self.add_action(investigation_menu, "Define Outbreak Case...", self.run_define_case, 'icons/define_case.svg')
        self.add_action(analysis_menu, "Epidemic Curve...", self.run_epi_curve, 'icons/epi_curve.svg')
        self.add_action(analysis_menu, "LISA Cluster Map...", self.run_lisa_analysis, 'icons/lisa_analysis.svg')
        analysis_menu.addSeparator()
        self.add_action(analysis_menu, "Create Report Map...", self.run_create_report_map, 'icons/create_map.svg')
        self.add_action(one_health_menu, "MCM OT: Coordination Mechanism Wizard...", self.run_mcm_wizard)
        self.add_action(one_health_menu, "JRA OT: Joint Risk Assessment Wizard...", self.run_jra_wizard)
        self.add_action(one_health_menu, "SIS OT: Surveillance & Info Sharing Wizard...", self.run_sis_wizard)
        self.add_action(planning_menu, "Surveillance Scheme Designer...", self.run_surveillance_designer)
        planning_menu.addSeparator()
        self.add_action(planning_menu, "SURVCosT: Surveillance Program Costing...", self.run_survcost)
        self.add_action(planning_menu, "OutCosT: Outbreak Impact Assessment...", self.run_outcost)
        self.add_action(planning_menu, "Economic Parameter Database...", self.run_edit_eco_params)
        tutorial_menu = training_menu.addMenu("Interactive Learning Modules")
        self.add_action(tutorial_menu, "Tutorial: Investigating an Outbreak", lambda: run_tutorial(self.iface, "Outbreak Investigation"))
        self.add_action(help_menu, "EADST Help & Resources...", self.run_help, 'icons/help.svg')
        self.add_action(help_menu, "About EADST...", self.show_about)

    def add_action(self, menu, text, callback, icon_path=None, is_toolbar=False):
        action = QAction(text, self.iface.mainWindow())
        if icon_path:
            action.setIcon(QIcon(os.path.join(self.plugin_dir, icon_path)))
        action.triggered.connect(callback)
        menu.addAction(action)
        if is_toolbar:
            self.toolbar.addAction(action)
        self.actions.append(action)
        return action

    def unload(self):
        self.iface.removePluginMenu(self.menu, self.eadst_menu)
        for action in self.actions:
            self.toolbar.removeAction(action)
        del self.toolbar
    
    # --- Callback Function Stubs ---
    def run_new_investigation(self): ProjectSetupWizard(self.iface.mainWindow()).exec_()
    def run_import_data(self): ImportDataDialog(self.iface.mainWindow()).exec_()
    def run_quality_dashboard(self): DataQualityDashboard(self.iface.mainWindow()).exec_()
    def run_anonymize_data(self): AnonymizeDataTool(self.iface.mainWindow()).exec_()
    def run_add_record(self): self.add_record_tool = AddRecordTool(self.iface); self.iface.mapCanvas().setMapTool(self.add_record_tool)
    def run_field_tracing(self): self.field_trace_tool = FieldTracingTool(self.iface); self.field_trace_tool.start_tracing()
    def run_define_case(self): CaseDefinitionDialog(self.iface.mainWindow()).exec_()
    def run_epi_curve(self): EpiCurveDialog(self.iface.mainWindow()).exec_()
    def run_lisa_analysis(self): LISAAnalysisDialog(self.iface.mainWindow()).exec_()
    def run_create_report_map(self): CreateReportMap(self.iface).show()
    def run_mcm_wizard(self): MCM_OT_Wizard(self.iface.mainWindow()).exec_()
    def run_jra_wizard(self): JRA_OT_Wizard(self.iface.mainWindow()).exec_()
    def run_sis_wizard(self): SIS_OT_Wizard(self.iface.mainWindow()).exec_()
    def run_surveillance_designer(self): SurveillanceDesigner(self.iface.mainWindow()).exec_()
    def run_survcost(self): SURVCosTDialog(self.iface.mainWindow()).exec_()
    def run_outcost(self): OutCosTDialog(self.iface.mainWindow()).exec_()
    def run_edit_eco_params(self): EconomicParametersDialog(self.iface.mainWindow()).exec_()
    def run_help(self):
        if self.help_dialog is None:
            self.help_dialog = HelpDialog(self.iface.mainWindow())
        self.help_dialog.show()
    def show_about(self): QMessageBox.about(self.iface.mainWindow(), "About EADST", "Ethiopian Animal Disease Surveillance Toolbox (EADST) v3.0")
EOL

# metadata.txt
cat > eadst_plugin/metadata.txt << 'EOL'
[general]
name=Ethiopian Animal Disease Surveillance Toolbox
qgisMinimumVersion=3.16
description=A holistic, integrated QGIS plugin for One Health management, surveillance design, and economic analysis in Ethiopia.
version=2.0.0
author=EADST Development Team
email=eadst.support@moa.gov.et
experimental=True
EOL

# --- Python Module Files ---
echo "  -> Creating placeholder Python scripts for all modules..."
touch eadst_plugin/modules/__init__.py
for module in project_setup data_management outbreak_investigation analysis_reporting surveillance_economics one_health_coordination training help utils; do
    echo "Creating eadst_plugin/modules/${module}.py"
    # Create specific placeholders for each module
    case $module in
        "one_health_coordination")
            cat > "eadst_plugin/modules/${module}.py" << 'EOT'
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
class MCM_OT_Wizard(QDialog):
    def __init__(self, parent=None): super().__init__(parent); self.setWindowTitle("MCM OT Wizard")
class JRA_OT_Wizard(QDialog):
    def __init__(self, parent=None): super().__init__(parent); self.setWindowTitle("JRA OT Wizard")
class SIS_OT_Wizard(QDialog):
    def __init__(self, parent=None): super().__init__(parent); self.setWindowTitle("SIS OT Wizard")
EOT
            ;;
        "training")
             cat > "eadst_plugin/modules/${module}.py" << 'EOT'
from qgis.core import Qgis
def run_tutorial(iface, tutorial_name):
    iface.messageBar().pushMessage("Info", f"Starting interactive tutorial: {tutorial_name}", level=Qgis.Success)
EOT
            ;;
        *)
            CLASS_NAME=$(echo "$module" | sed -r 's/(^|_)(\w)/\U\2/g' | sed 's/_//g')Dialog
            cat > "eadst_plugin/modules/${module}.py" << EOT
# Placeholder for ${module} module
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout
class ${CLASS_NAME}(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("${module//_/ }".title())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Functionality for ${module//_/ } to be implemented here."))
EOT
            # Add other necessary classes for modules with multiple tools
            if [ "$module" = "project_setup" ]; then echo "class ProjectSetupWizard(QDialog): pass" >> "eadst_plugin/modules/${module}.py"; fi
            if [ "$module" = "data_management" ]; then echo -e "class DataQualityDashboard(QDialog): pass\nclass AnonymizeDataTool(QDialog): pass" >> "eadst_plugin/modules/${module}.py"; fi
            ;;
    esac
done

# Create other necessary files and folders
mkdir -p eadst_plugin/providers && touch eadst_plugin/providers/__init__.py
mkdir -p eadst_plugin/resources/base_layers && touch eadst_plugin/resources/base_layers/placeholder.txt
mkdir -p eadst_plugin/ui && touch eadst_plugin/ui/placeholder.txt
mkdir -p tests && touch tests/__init__.py
mkdir -p docs && touch docs/placeholder.md
touch eadst_plugin/resources.qrc
touch eadst_plugin/providers/pysal_provider.py
touch .gitignore LICENSE README.md

# --- Create placeholder icons ---
echo "  -> Creating placeholder SVG icons..."
for icon_name in eadst_icon new_project import_data quality_dashboard anonymize_data add_record field_tracing define_case epi_curve lisa_analysis create_map surveillance_designer survcost outcost economic_params help about; do
    cat > "eadst_plugin/icons/${icon_name}.svg" << EOL
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle></svg>
EOL
done

echo "---------------------------------------------"
echo "Project structure for '$ROOT_DIR' created successfully."
echo "Remember to:"
echo "  1. Replace placeholder scripts with full, functional code."
echo "  2. Add real icon files (.svg) to 'eadst_plugin/icons/'"
echo "  3. Add base layer shapefiles to 'eadst_plugin/resources/base_layers/'"
echo "  4. Create and populate 'eadst_plugin/resources/data_standard.db'."
echo "  5. Add PDF documents to the 'docs/' folder."
echo "---------------------------------------------"
