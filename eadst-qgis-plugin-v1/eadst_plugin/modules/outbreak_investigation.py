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
