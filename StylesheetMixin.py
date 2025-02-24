import os
import sys
from PyQt5.QtWidgets import QMessageBox

class StylesheetMixin:
    def apply_stylesheet(self, prefix: str = "custom"):
        stylesheet_path = self.get_default_stylesheet_path(prefix)
        try:
            with open(stylesheet_path, 'r') as file:
                self.setStyleSheet(file.read())
        except Exception as e:
            QMessageBox.warning(self, "Style Error", f"Failed to apply stylesheet: {e}")

    def get_default_stylesheet_path(self, prefix: str = "custom"):
        # Determine the base path (works with frozen executables)
        base_path = sys._MEIPASS if hasattr(sys, 'frozen') else os.path.dirname(__file__)
        custom_path = os.path.join(base_path, f'{prefix}style.qss')
        # Ensure self.settings exists before accessing it
        if os.path.exists(custom_path) and getattr(self, 'settings', None) and self.settings.get('UI', 'custom_theming'):
            return custom_path
        return os.path.join(base_path, 'style.qss')