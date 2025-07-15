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
