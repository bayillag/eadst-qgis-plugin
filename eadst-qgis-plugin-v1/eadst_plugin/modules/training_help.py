from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
def run_tutorial(iface, tutorial_name):
    iface.messageBar().pushMessage("Info", f"Starting interactive tutorial: {tutorial_name}")
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EADST Help & Resources")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Searchable glossary and data standard browser."))
