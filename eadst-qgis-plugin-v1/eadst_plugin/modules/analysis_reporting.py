from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel
class EpiCurveDialog(QDialog): pass
class AttackRateDialog(QDialog): pass
class LISAAnalysisDialog(QDialog): pass
class CreateReportMap:
    def __init__(self, iface): self.iface = iface
    def show(self): self.iface.messageBar().pushMessage("Info", "Opening Print Layout with EADST template...")
