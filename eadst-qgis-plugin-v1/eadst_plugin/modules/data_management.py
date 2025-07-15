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
