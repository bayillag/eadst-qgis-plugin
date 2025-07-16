# Placeholder for help module
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("help".title())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Functionality for help to be implemented here."))

# eadst_plugin/modules/help.py

import os
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QWidget, QTabWidget, QLabel, 
                                 QLineEdit, QTextBrowser, QTableWidget, QTableWidgetItem, 
                                 QHeaderView, QPushButton, QGridLayout)
from .utils import get_all_from_table, open_pdf

# This dictionary would ideally be loaded from a file or database
GLOSSARY_TERMS = {
    "Attack Rate": "A measurement of the proportion of animals in a population that experience an acute health event during a limited period (e.g., during an outbreak).",
    "Case Definition": "A set of standard criteria for classifying whether an animal has a particular disease, syndrome, or other health condition.",
    "Inference Group": "The group of units (e.g., premises, animals) that the surveillance provides information about.",
    "LISA": "Local Indicators of Spatial Association. A statistical method to identify the location of statistically significant spatial clusters and outliers.",
    "DALY": "Disability-Adjusted Life Year. A measure of overall disease burden, expressed as the number of years lost due to ill-health, disability or early death.",
    "Surveillance Scheme": "A documented plan that describes all aspects of a surveillance activity, including its objectives, methods, and analysis plan."
}

class HelpDialog(QDialog):
    """A comprehensive, non-modal dialog for help, resources, and training."""
    def __init__(self, iface, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("EADST Help & Resources")
        self.setMinimumSize(800, 650)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_glossary_tab(), "Glossary")
        self.tabs.addTab(self.create_data_standard_tab(), "Data Standard Browser")
        self.tabs.addTab(self.create_docs_tab(), "Source Documents")
        
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_glossary_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for a term (e.g., LISA, Attack Rate)...")
        self.search_bar.textChanged.connect(self.filter_glossary)
        
        self.results_browser = QTextBrowser()
        
        layout.addWidget(self.search_bar)
        layout.addWidget(self.results_browser)
        widget.setLayout(layout)
        self.filter_glossary("") # Populate initially
        return widget

    def filter_glossary(self, text):
        self.results_browser.clear()
        html_content = ""
        for term, definition in sorted(GLOSSARY_TERMS.items()):
            if text.lower() in term.lower():
                html_content += f"<h3>{term}</h3><p>{definition}</p><hr>"
        self.results_browser.setHtml(html_content)

    def create_data_standard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        standard_tabs = QTabWidget()
        # Add a tab for each key table in the data standard
        standard_tabs.addTab(self.create_db_table_view("diseases", "disease_name"), "Diseases")
        standard_tabs.addTab(self.create_db_table_view("breeds", "breed_name"), "Breeds")
        standard_tabs.addTab(self.create_db_table_view("vaccines", "vaccine_name"), "Vaccines")
        standard_tabs.addTab(self.create_db_table_view("diagnostics", "method_name"), "Diagnostics")
        
        layout.addWidget(standard_tabs)
        widget.setLayout(layout)
        return widget

    def create_db_table_view(self, table_name, order_by_col):
        """Creates a QWidget containing a QTableWidget populated from the DB."""
        widget = QWidget()
        layout = QVBoxLayout()
        table = QTableWidget()
        layout.addWidget(table)
        widget.setLayout(layout)
        
        headers, data = get_all_from_table(table_name, order_by_col)
        
        if headers:
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels([h.replace("_", " ").title() for h in headers])
            table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
            table.resizeColumnsToContents()
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            layout.addWidget(QLabel(f"Could not load data for '{table_name}'. Is the database configured?"))
            
        return widget

    def create_docs_tab(self):
        """Creates a tab with buttons to open key reference documents."""
        widget = QWidget()
        layout = QGridLayout()
        
        docs_to_link = {
            "Ethiopian National Livestock Data Standard": "Ethiopian_National_Livestock_Data_Standard.pdf",
            "USDA Surveillance Design Guide": "Guidance_on_How_to_Design_a_Surveillance_Scheme.pdf",
            "AU-IBAR Surveillance Manual": "Manual_of_Basic_Animal_Disease_Surveillance.pdf",
            "OIE PVS Laboratory Mission Report": "PVS_Laboratory_Mission_Report_Kyrgyz.pdf",
            "FAO ASL2050 Ethiopia Report": "Livestock_health_livelihoods_and_the_environment_in_Ethiopia.pdf",
            "Tripartite Zoonoses Guide - MCM OT": "Multisectoral_Coordination_Mechanisms_Operational_Tool.pdf"
        }
        
        row, col = 0, 0
        for doc_title, doc_filename in docs_to_link.items():
            button = QPushButton(doc_title)
            button.clicked.connect(lambda checked, fn=doc_filename: open_pdf(fn))
            layout.addWidget(button, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        widget.setLayout(layout)
        return widget