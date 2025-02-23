from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout
)

from StylesheetMixin import StylesheetMixin

class NewCanvasDialog(QDialog, StylesheetMixin):
    def __init__(self, width: int = 640, height: int = 480):
        super().__init__()
        self.apply_stylesheet()
        self.setWindowTitle('New Canvas')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form_layout = QFormLayout()
        self.layout.addLayout(form_layout)

        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width")
        self.width_input.setText(str(width))
        self.width_input.setValidator(QIntValidator())
        form_layout.addRow("Width", self.width_input)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height")
        self.height_input.setText(str(height))
        self.height_input.setValidator(QIntValidator())
        form_layout.addRow("Height", self.height_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)