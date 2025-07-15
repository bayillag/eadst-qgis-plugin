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
