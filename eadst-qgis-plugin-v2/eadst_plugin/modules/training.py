from qgis.core import Qgis
def run_tutorial(iface, tutorial_name):
    iface.messageBar().pushMessage("Info", f"Starting interactive tutorial: {tutorial_name}", level=Qgis.Success)

# eadst_plugin/modules/training.py

import os
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QWidget, QTextBrowser)
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject
from .utils import get_plugin_path, show_message

# --- Tutorial Definitions ---
# This dictionary holds the steps for each tutorial.
# It makes adding new tutorials simple.
TUTORIALS = {
    "Outbreak Investigation": [
        "Welcome! This tutorial will guide you through investigating a new outbreak. A sample project has been loaded for you.",
        "Step 1: Inspect the data. Right-click on the 'sample_outbreaks' layer in the Layers Panel and select 'Open Attribute Table'.",
        "Step 2: Let's visualize the timeline. Go to 'EADST -> Analysis & Reporting -> Descriptive Epidemiology -> Generate Epidemic Curve'.",
        "Step 3: Select the 'sample_outbreaks' layer and the 'Event_Date' field. Aggregate by 'Day' and click OK.",
        "Step 4: Now, let's find hotspots. Go to 'EADST -> Analysis & Reporting -> Spatial Analysis -> Hotspot Map (Kernel Density)'.",
        "Step 5: Use the 'sample_outbreaks' layer as input and set a Radius of 50000 meters. Run the tool.",
        "Congratulations! You have completed the basic outbreak investigation tutorial."
    ]
}

class TutorialStepWidget(QWidget):
    """A non-modal widget that displays tutorial steps."""
    def __init__(self, title, steps, parent=None):
        super(TutorialStepWidget, self).__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # Keep on top of QGIS
        self.steps = steps
        self.current_step = 0

        # UI Elements
        self.instruction_browser = QTextBrowser()
        self.btn_prev = QPushButton("<< Previous")
        self.btn_next = QPushButton("Next >>")
        self.btn_close = QPushButton("Close Tutorial")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.instruction_browser)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_prev)
        hbox.addWidget(self.btn_next)
        layout.addLayout(hbox)
        layout.addWidget(self.btn_close)
        self.setLayout(layout)

        # Connections
        self.btn_next.clicked.connect(self.next_step)
        self.btn_prev.clicked.connect(self.prev_step)
        self.btn_close.clicked.connect(self.close)

        self.update_display()

    def update_display(self):
        self.instruction_browser.setHtml(f"<h3>Step {self.current_step + 1}/{len(self.steps)}</h3>"
                                         f"<p>{self.steps[self.current_step]}</p>")
        self.btn_prev.setEnabled(self.current_step > 0)
        self.btn_next.setEnabled(self.current_step < len(self.steps) - 1)

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_display()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_display()


class TutorialManager:
    """Manages the loading and running of a tutorial session."""
    def __init__(self, iface, tutorial_name):
        self.iface = iface
        self.tutorial_name = tutorial_name
        self.widget = None

    def start(self):
        if self.tutorial_name not in TUTORIALS:
            show_message(self.iface, f"Tutorial '{self.tutorial_name}' not found.", level=Qgis.Critical)
            return

        # Load the sample project for the tutorial
        project_path = os.path.join(get_plugin_path(), "..", "sample_project", "EADST_Tutorial_1.qgz")
        if not os.path.exists(project_path):
            show_message(self.iface, f"Sample project not found: {project_path}", level=Qgis.Critical)
            return
            
        QgsProject.instance().read(project_path)
        show_message(self.iface, "Sample project loaded.", level=Qgis.Success)

        # Create and show the step widget
        steps = TUTORIALS[self.tutorial_name]
        self.widget = TutorialStepWidget(f"Tutorial: {self.tutorial_name}", steps, self.iface.mainWindow())
        self.widget.show()


def run_tutorial(iface, tutorial_name):
    """Entry point function to start a tutorial."""
    # The manager is instantiated but not stored, its widget will live on its own.
    tutorial_manager = TutorialManager(iface, tutorial_name)
    tutorial_manager.start()