from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout,
    QColorDialog, QComboBox, QPushButton
)

from StylesheetMixin import StylesheetMixin

class NewCanvasDialog(QDialog, StylesheetMixin):
    def __init__(self, width: int = 640, height: int = 480):
        super().__init__()
        self.apply_stylesheet('bb')
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

        self.color_mode_dropdown = QComboBox()
        self.color_mode_dropdown.addItems(["Dark", "Light", "Custom Color"])
        form_layout.addRow("Canvas Color", self.color_mode_dropdown)

        self.color_picker_button = QPushButton("Select Color")
        self.color_picker_button.setVisible(False)
        self.color_picker_button.setEnabled(False)
        form_layout.addRow("", self.color_picker_button)

        self.color_mode_dropdown.currentIndexChanged.connect(self.on_color_mode_change)
        self.color_picker_button.clicked.connect(self.select_custom_color)
        
        self.selected_color = ("Dark", None)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

    def on_color_mode_change(self):
        if self.color_mode_dropdown.currentText() == "Custom Color":
            self.color_picker_button.setVisible(True)
            self.color_picker_button.setEnabled(True)
        else:
            self.color_picker_button.setVisible(False)
            self.color_picker_button.setEnabled(False)
            self.selected_color = (self.color_mode_dropdown.currentText(), None)
    
    def select_custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = ("Custom Color", color.name())
        else:
            self.selected_color = ("Dark", None)
