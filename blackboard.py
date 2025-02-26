import sys
import time
from PyQt5.QtCore import Qt #, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImageReader
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QAction, QWidget,
    QDialog, QMessageBox, QSizePolicy, QPushButton, QScrollArea, QSlider,
    QFileDialog
)
import dialogs
from canvasObjects import (
    JCanvas, JPaletteButton, JCanvasContainer
)
from StylesheetMixin import StylesheetMixin

DARKCOLORS = [
    '#ffffff', '#fff44f', '#ffb6c1', '#6ec6ff',
    '#77dd77', '#c3a6ff', '#ffb347', '#ff6961'
]
LIGHTCOLORS = [
    '#000000', '#0000ff', '#800080', '#008000',
    '#ff0000', '#ffa500', '#a52a2a', '#ffd700'
]

class Blackboard(QMainWindow, StylesheetMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Blackboard')
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(480, 360)
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        self.apply_stylesheet(prefix='bb')
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout()
        main_widget.setLayout(self.main_layout)

        # Menu Bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu('File')

        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_action)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)

        open_action = QAction('Open', self)
        open_action.triggered.connect(self.load_action)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(lambda: self.save_as() if self.current_file == None else self.save_action())
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)

        save_action = QAction('Save As', self)
        save_action.triggered.connect(lambda: self.save_as())
        save_action.setShortcut('Ctrl+Shift+S')
        file_menu.addAction(save_action)

        edit_menu = self.menu_bar.addMenu('Edit')

        undo_action = QAction('Undo', self)
        undo_action.triggered.connect(self.undo)
        undo_action.setShortcut('Ctrl+Z')
        edit_menu.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.triggered.connect(self.redo)
        redo_action.setShortcut('Ctrl+Shift+Z')
        edit_menu.addAction(redo_action)

        # Main UI
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        
        self.canvas = JCanvas()
        self.canvas.wheelScrolled.connect(self.scroll_on_canvas)
        self.scroll_area = JCanvasContainer(self.canvas)
        layout.addWidget(self.scroll_area)

        # Tools
        tools = QScrollArea()
        tools_layout = QHBoxLayout()
        
        self.palette = QHBoxLayout()
        self.palette.setAlignment(Qt.AlignLeft)
        tools_layout.addLayout(self.palette)

        tool_selector = QHBoxLayout()
        tool_selector.setAlignment(Qt.AlignLeft)
        tools_layout.addLayout(tool_selector)

        pen_tool = QPushButton('Pen')
        pen_tool.setShortcut('P')
        pen_tool.setToolTip('<b>Pen (P):</b> Freehand drawing tool.')
        pen_tool.clicked.connect(lambda: self.canvas.set_tool('pen'))
        tool_selector.addWidget(pen_tool)

        eraser_tool = QPushButton('Eraser')
        eraser_tool.setShortcut('Shift+P')
        eraser_tool.setToolTip('<b>Eraser (Shift+P):</b> Erase parts of the drawing.')
        eraser_tool.clicked.connect(lambda: self.canvas.set_tool('eraser'))
        tool_selector.addWidget(eraser_tool)

        rectangle_tool = QPushButton('Rectangle')
        rectangle_tool.setShortcut('R')
        rectangle_tool.setToolTip('<b>Rectangle (R):</b> Draw rectangular shapes.')
        rectangle_tool.clicked.connect(lambda: self.canvas.set_tool('rectangle'))
        tool_selector.addWidget(rectangle_tool)

        ellipse_tool = QPushButton('Ellipse')
        ellipse_tool.setShortcut('E')
        ellipse_tool.setToolTip('<b>Ellipse (E):</b> Draw elliptical shapes.')
        ellipse_tool.clicked.connect(lambda: self.canvas.set_tool('ellipse'))
        tool_selector.addWidget(ellipse_tool)

        line_tool = QPushButton('Line')
        line_tool.setShortcut('L')
        line_tool.setToolTip('<b>Line (L):</b> Draw straight lines.')
        line_tool.clicked.connect(lambda: self.canvas.set_tool('line'))
        tool_selector.addWidget(line_tool)

        self.width_slider = QSlider()
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(50)
        self.width_slider.setValue(4)
        self.width_slider.setOrientation(Qt.Horizontal)
        self.width_slider.valueChanged.connect(lambda: self.canvas.set_tool_width(self.width_slider.value()))
        tools_layout.addWidget(self.width_slider)

        self.add_palette_buttons(self.palette, DARKCOLORS)

        palette_widget = QWidget()
        palette_widget.setLayout(tools_layout)
        palette_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  
        palette_widget.setFixedHeight(palette_widget.sizeHint().height())
        
        tools.setWidget(palette_widget)
        tools.setWidgetResizable(False)

        tools.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(tools)

        self.setCentralWidget(widget)

    def undo(self):
        self.canvas.undo()

    def redo(self):
        self.canvas.redo()

    def scroll_on_canvas(self, direction, crtl_pressed):
        if crtl_pressed:
          if direction == 1:
              pass
          elif direction == -1:
              pass
        else:
            if direction == 1:
                if self.width_slider.value() in range(1,50):
                    self.width_slider.setValue(self.width_slider.value() + 1)
            elif direction == -1:
                if self.width_slider.value() in range(2,51):
                    self.width_slider.setValue(self.width_slider.value() - 1)

    def add_palette_buttons(self, layout, colors):
        # Clear existing palette buttons if they exist
        for i in reversed(range(layout.count())): 
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
                # item.widget().deleteLater()

        # Add new palette buttons
        for i in range(0, len(colors)):
            button = JPaletteButton(colors[i])
            button.pressed.connect(lambda color=colors[i]: self.canvas.set_pen_color(color))
            if i < 10:
                button.setShortcut(f'{i+1}')
            elif i == 10:
                button.setShortcut(f'0')
            layout.addWidget(button)

        rainbow_button = JPaletteButton()
        rainbow_button.pressed.connect(lambda: self.canvas.set_pen_color())
        layout.addWidget(rainbow_button)

    def new_action(self):
        self.current_file = None
        pen_color = self.canvas.pen_color
        dialog = dialogs.NewCanvasDialog(self.canvas.width, self.canvas.height)
        if dialog.exec_() == QDialog.Accepted:
            try:
                width = int(dialog.width_input.text())
                height = int(dialog.height_input.text())
            except ValueError:
                QMessageBox.critical(self, "Value Error", "Both the height and width must be entered to create a new canvas.")
                return
            color = '#ffffff' if dialog.selected_color[0] == 'Light' else dialog.selected_color[1] if dialog.selected_color[0] == 'Custom Color' else '#1c1c1c'
            new_canvas = JCanvas(width, height, color)
            self.add_palette_buttons(self.palette, DARKCOLORS if new_canvas.color.getHsl()[2] < 128 else LIGHTCOLORS)
            self.canvas = new_canvas
            self.canvas.wheelScrolled.connect(self.scroll_on_canvas)
            self.scroll_area.set_canvas(self.canvas)
            self.canvas.clear()
            self.canvas.set_tool('pen')
            self.canvas.set_tool_width(self.width_slider.value())
            self.canvas.set_pen_color(pen_color)

    def load_action(self):
        pen_color = self.canvas.pen_color
        options = QFileDialog.Options()
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Image Files (*.png);;All Files (*)", options=options)
            if filename:
                reader = QImageReader(filename)
                metadata_color = reader.text("canvas_color")  # Extract metadata

                # Default to dark if no color metadata is found
                canvas_color = metadata_color if metadata_color else "#1c1c1c"

                new_canvas = JCanvas(loadedImage=QPixmap(filename), color=canvas_color)
                self.add_palette_buttons(self.palette, DARKCOLORS if new_canvas.color.getHsl()[2] < 128 else LIGHTCOLORS)
                self.canvas = new_canvas
                self.canvas.wheelScrolled.connect(self.scroll_on_canvas)
                self.scroll_area.set_canvas(self.canvas)
                self.canvas.set_tool('pen')
                self.canvas.set_tool_width(self.width_slider.value())
                self.canvas.set_pen_color(pen_color)
                self.current_file = filename
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def save_action(self):
        if self.current_file == None: return
        self.canvas.save(self.current_file, "blackboard")

    def save_as(self):
        options = QFileDialog.Options()
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Image Files (*.png);;All Files (*)", options=options)
            if filename:
                self.current_file = filename
                self.save_action()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open file: {e}")
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    blackboard = Blackboard()
    blackboard.show()
    sys.exit(app.exec_())