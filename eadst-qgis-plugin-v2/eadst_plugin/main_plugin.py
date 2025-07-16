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



"""
# eadst_plugin/main_plugin.py

import os
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon

# Import only the specific classes needed
from .modules.project_setup import ProjectSetupWizard, ImportDataDialog
# ... other imports ...

class EADSTPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = "&EADST"
        self.toolbar = self.iface.addToolBar("EADST Toolbar")
        self.toolbar.setObjectName("EADSTToolbar")
        self.help_dialog = None # Keep this for other modules

    def initGui(self):
        """Create all menus and toolbar actions."""
        self.eadst_menu = QMenu(self.menu, self.iface.mainWindow().menuBar())
        self.iface.mainWindow().menuBar().insertMenu(self.iface.pluginMenu().actions()[0], self.eadst_menu)

        # --- Project Setup Menu ---
        setup_menu = self.eadst_menu.addMenu("Project Setup")
        self.add_action(setup_menu, "New Investigation Project...", self.run_new_investigation, 'icons/new_project.svg', is_toolbar=True)
        # Assuming the data management menu will be created next
        # self.add_action(setup_menu, "Import Standardized Data...", self.run_import_data, 'icons/import_data.svg')
        
        # ... Add other menus here ...

    def add_action(self, menu, text, callback, icon_path=None, is_toolbar=False):
        action = QAction(text, self.iface.mainWindow())
        if icon_path:
            action.setIcon(QIcon(os.path.join(self.plugin_dir, icon_path)))
        action.triggered.connect(callback)
        menu.addAction(action)
        if is_toolbar:
            self.toolbar.addAction(action)
        self.actions.append(action)

    def unload(self):
        """Removes the plugin menu and toolbar."""
        self.iface.removePluginMenu(self.menu, self.eadst_menu)
        for action in self.actions:
            self.toolbar.removeAction(action)
        if hasattr(self, 'toolbar'):
            del self.toolbar

    # --- Callback Functions ---
    def run_new_investigation(self):
        """Run the New Investigation Wizard."""
        wizard = ProjectSetupWizard(self.iface.mainWindow())
        wizard.exec_()

    def run_import_data(self):
        """Run the Import Data Dialog."""
        dialog = ImportDataDialog(self.iface.mainWindow())
        dialog.exec_()

    # ... other callback functions for other menus ...
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.data_management import ImportDataDialog, DataQualityDashboard, AnonymizeDataTool

class EADSTPlugin:
    # ... (__init__ and other methods) ...

    def initGui(self):
        # ... (menu setup as before) ...
        data_mgmt_menu = self.eadst_menu.addMenu("Data Management")
        
        self.add_action(data_mgmt_menu, "Import Standardized Data...", self.run_import_data, 'icons/import_data.svg')
        self.add_action(data_mgmt_menu, "Data Quality Dashboard...", self.run_quality_dashboard, 'icons/quality_dashboard.svg')
        self.add_action(data_mgmt_menu, "Anonymize Case Data...", self.run_anonymize_data, 'icons/anonymize_data.svg')
        
        # ... rest of initGui ...

    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    # ... (previous callbacks) ...
    def run_import_data(self):
        dialog = ImportDataDialog(self.iface.mainWindow())
        dialog.exec_()

    def run_quality_dashboard(self):
        dialog = DataQualityDashboard(self.iface.mainWindow())
        dialog.exec_()
    
    def run_anonymize_data(self):
        dialog = AnonymizeDataTool(self.iface.mainWindow())
        dialog.exec_()
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.outbreak_investigation import AddRecordTool, FieldTracingTool, CaseDefinitionDialog

class EADSTPlugin:
    # ... (__init__ and other methods) ...

    def initGui(self):
        # ... (menu setup as before) ...
        investigation_menu = self.eadst_menu.addMenu("Outbreak Investigation")
        
        self.add_action(investigation_menu, "Add Outbreak Record...", self.run_add_record, 'icons/add_record.svg', is_toolbar=True)
        self.add_action(investigation_menu, "Field Tracing Tool", self.run_field_tracing, 'icons/field_tracing.svg', is_toolbar=True)
        investigation_menu.addSeparator()
        self.add_action(investigation_menu, "Define Outbreak Case...", self.run_define_case, 'icons/define_case.svg')
        
        # ... rest of initGui ...

    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    # ... (previous callbacks) ...
    def run_add_record(self):
        """Activates the tool to add a new record by clicking the map."""
        self.add_record_tool = AddRecordTool(self.iface)
        self.iface.mapCanvas().setMapTool(self.add_record_tool)
        show_message(self.iface, "Click on the map to place a new outbreak record.", duration=5)

    def run_field_tracing(self):
        """Initializes the field tracing tool."""
        self.field_trace_tool = FieldTracingTool(self.iface)
        self.field_trace_tool.start_tracing()
        
    def run_define_case(self):
        dialog = CaseDefinitionDialog(self.iface, self.iface.mainWindow())
        dialog.exec_()
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.analysis_reporting import EpiCurveDialog, AttackRateDialog, LISAAnalysisDialog, CreateReportMap

class EADSTPlugin:
    # ... (__init__ and other methods) ...

    def initGui(self):
        # ... (menu setup as before) ...
        analysis_menu = self.eadst_menu.addMenu("Analysis & Reporting")
        
        desc_epi_menu = analysis_menu.addMenu("Descriptive Epidemiology")
        self.add_action(desc_epi_menu, "Generate Epidemic Curve...", self.run_epi_curve)
        self.add_action(desc_epi_menu, "Calculate Attack Rates...", self.run_attack_rates)

        spatial_analysis_menu = analysis_menu.addMenu("Spatial Pattern Analysis")
        self.add_action(spatial_analysis_menu, "Local Cluster Analysis (LISA)...", self.run_lisa_analysis)
        # Add other spatial tools here...
        
        analysis_menu.addSeparator()
        self.add_action(analysis_menu, "Create Report Map...", self.run_create_report_map)
        
    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    def run_epi_curve(self):
        dialog = EpiCurveDialog(self.iface.mainWindow())
        dialog.exec_()

    def run_attack_rates(self):
        dialog = AttackRateDialog(self.iface.mainWindow())
        dialog.exec_()
        
    def run_lisa_analysis(self):
        dialog = LISAAnalysisDialog(self.iface.mainWindow())
        dialog.exec_()
    
    def run_create_report_map(self):
        tool = CreateReportMap(self.iface)
        tool.show()
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.one_health_coordination import MCM_OT_Wizard, JRA_OT_Wizard, SIS_OT_Wizard

class EADSTPlugin:
    # ... (__init__ and other methods) ...

    def initGui(self):
        # ... (setup for other menus) ...
        one_health_menu = self.eadst_menu.addMenu("One Health Coordination")
        
        self.add_action(one_health_menu, "MCM OT: Coordination Mechanism Wizard...", self.run_mcm_wizard)
        self.add_action(one_health_menu, "JRA OT: Joint Risk Assessment Wizard...", self.run_jra_wizard)
        self.add_action(one_health_menu, "SIS OT: Surveillance & Info Sharing Wizard...", self.run_sis_wizard)
        
        # ... rest of initGui ...

    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    # ... (previous callbacks) ...
    def run_mcm_wizard(self):
        wizard = MCM_OT_Wizard(self.iface.mainWindow())
        wizard.exec_()
    
    def run_jra_wizard(self):
        wizard = JRA_OT_Wizard(self.iface.mainWindow())
        wizard.exec_()
        
    def run_sis_wizard(self):
        dialog = SIS_OT_Wizard(self.iface.mainWindow())
        dialog.exec_()
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.surveillance_economics import (SurveillanceDesigner, SURVCosTDialog, 
                                             OutCosTDialog, EconomicParametersDialog)

class EADSTPlugin:
    # ... (__init__ and other methods) ...

    def initGui(self):
        # ... (menu setup as before) ...
        planning_menu = self.eadst_menu.addMenu("Surveillance & Economics")
        
        self.add_action(planning_menu, "Surveillance Scheme Designer...", self.run_surveillance_designer)
        planning_menu.addSeparator()
        self.add_action(planning_menu, "SURVCosT: Surveillance Program Costing...", self.run_survcost)
        self.add_action(planning_menu, "OutCosT: Outbreak Impact Assessment...", self.run_outcost)
        planning_menu.addSeparator()
        self.add_action(planning_menu, "Economic Parameter Database...", self.run_edit_eco_params)
        
        # ... rest of initGui ...

    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    # ... (previous callbacks) ...
    def run_surveillance_designer(self):
        wizard = SurveillanceDesigner(self.iface.mainWindow())
        wizard.exec_()
    
    def run_survcost(self):
        dialog = SURVCosTDialog(self.iface.mainWindow())
        dialog.exec_()
        
    def run_outcost(self):
        dialog = OutCosTDialog(self.iface.mainWindow())
        dialog.exec_()

    def run_edit_eco_params(self):
        dialog = EconomicParametersDialog(self.iface.mainWindow())
        dialog.exec_()
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.training import run_tutorial
from .modules.help import HelpDialog # Assuming help is in a separate module

class EADSTPlugin:
    # ... (__init__ and other methods) ...

    def initGui(self):
        # ... (setup for all other menus) ...
        training_menu = self.eadst_menu.addMenu("Training")
        
        tutorial_menu = training_menu.addMenu("Interactive Learning Modules")
        self.add_action(
            tutorial_menu, 
            "Tutorial: Investigating an Outbreak", 
            lambda: run_tutorial(self.iface, "Outbreak Investigation")
        )
        # Add a placeholder for the second tutorial
        self.add_action(
            tutorial_menu,
            "Tutorial: Designing a Surveillance Scheme",
            lambda: show_message(self.iface, "This tutorial is under development.")
        )
        
        help_menu = self.eadst_menu.addMenu("Help")
        self.add_action(help_menu, "EADST Help & Resources...", self.run_help, 'icons/help.svg')
        self.add_action(help_menu, "About EADST...", self.show_about)

    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    # ... (previous callbacks) ...
    def run_help(self):
        """Shows the main help dialog."""
        if self.help_dialog is None:
            self.help_dialog = HelpDialog(self.iface.mainWindow())
        self.help_dialog.show()
        self.help_dialog.raise_()
        self.help_dialog.activateWindow()

    def show_about(self):
        QMessageBox.about(self.iface.mainWindow(), "About EADST",
            "Ethiopian Animal Disease Surveillance Toolbox (EADST) v2.0\n\n"
            "An integrated QGIS plugin for animal health professionals.")
"""

"""
# eadst_plugin/main_plugin.py
# ... (previous imports)
from .modules.help import HelpDialog
# ... (and other module imports)

class EADSTPlugin:
    def __init__(self, iface):
        # ... (rest of __init__) ...
        self.help_dialog = None # Attribute to hold the dialog instance

    def initGui(self):
        # ... (setup for all other menus) ...
        
        help_menu = self.eadst_menu.addMenu("Help")
        self.add_action(help_menu, "EADST Help & Resources...", self.run_help, 'icons/help.svg')
        self.add_action(help_menu, "About EADST...", self.show_about)
        
    # ... (unload and add_action methods) ...

    # --- Callback Functions ---
    # ... (all previous callbacks) ...
    
    def run_help(self):
        """Shows the main help dialog, creating it if it doesn't exist."""
        # This pattern ensures only one instance of the dialog is created
        if self.help_dialog is None:
            # Pass the main window as parent
            self.help_dialog = HelpDialog(self.iface, self.iface.mainWindow())
        
        self.help_dialog.show()
        # Bring window to the front
        self.help_dialog.raise_()
        self.help_dialog.activateWindow()

    def show_about(self):
        QMessageBox.about(self.iface.mainWindow(), "About EADST",
            "Ethiopian Animal Disease Surveillance Toolbox (EADST) v3.0\n\n"
            "An integrated QGIS plugin for animal health professionals.\n"
            "Developed to support the Ethiopian National Livestock Data Standard.")

"""