from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import (
    QFont, QPixmap, QColor, QPainter, QBrush, QConicalGradient
)
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout,
    QColorDialog
)

class JCanvas(QLabel):
    def __init__(self, width: int = 640, height: int = 480, color: str = '#1c1c1c', loadedImage: QPixmap = None):
        super().__init__()
        self.width = width
        self.height = height
        self.color = QColor(color)
        self.tool = "pen"
        self.toolWidth = 4
        self.use_pressure = True  # Enable pressure sensitivity
        self.history = []  # Stack to store undo history
        self.max_history = 10  # Limit history size

        if loadedImage is not None and not loadedImage.isNull():
            self.pixmap = loadedImage.copy()
        else:
            self.pixmap = QPixmap(width, height)
            self.pixmap.fill(self.color)
        self.setPixmap(self.pixmap)

        self.last_x, self.last_y = None, None
        self.pen_color = QColor('#ffffff')

    def save_state(self):
        if len(self.history) >= self.max_history:
            self.history.pop(0)  # Remove oldest state if history limit is exceeded
        self.history.append(self.pixmap.copy())

    def undo(self):
        if self.history:
            self.pixmap = self.history.pop()
            self.setPixmap(self.pixmap)
            self.update()

    def clear(self):
        self.save_state()
        self.pixmap.fill(QColor(self.color))
        self.setPixmap(self.pixmap)
        self.update()

    def save(self, filename: str):
        self.pixmap.save(filename)

    def set_pen_color(self, color: str = None):
        if not color:
            colorpick = QColorDialog.getColor()
            if colorpick.isValid():
                self.pen_color = QColor(colorpick.name())
        else:
            self.pen_color = QColor(color)

    def set_tool_width(self, width: int = 4):
        self.toolWidth = width

    def set_tool(self, tool: str = "pen"):
        """Valid Tools: "pen", "eraser" """
        self.tool = tool

    def mousePressEvent(self, e):
        self.save_state()  # Save state before starting a new stroke
        self.last_x, self.last_y = e.x(), e.y()

    def mouseMoveEvent(self, e):
        if self.last_x is None:
            return

        pressure = e.pressure() if hasattr(e, 'pressure') and self.use_pressure else 1.0
        dynamic_width = max(1, round(self.toolWidth * pressure))

        pixmap = self.pixmap.copy()
        painter = QPainter(pixmap)
        p = painter.pen()
        if self.tool == 'pen':
            p.setColor(self.pen_color)
            p.setWidth(dynamic_width)
            p.setCapStyle(Qt.RoundCap)
        elif self.tool == 'eraser':
            p.setColor(self.color)
            p.setWidth(round(dynamic_width * 1.5))
            p.setCapStyle(Qt.RoundCap)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()

        self.setPixmap(pixmap)
        self.pixmap = pixmap.copy()
        self.update()

        self.last_x, self.last_y = e.x(), e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def tabletEvent(self, event):
        if event.type() == QEvent.TabletMove:
            self.use_pressure = True
            self.mouseMoveEvent(event)
        event.accept()

class JPaletteButton(QPushButton):
    def __init__(self, color: str = None):
        super().__init__()
        self.setFixedSize(QSize(24, 24))
        if color is not None:
            self.color = color
            self.setStyleSheet(f'background-color: {color};')
        else:
            self.color = None  # Default to None for gradient

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.color is None:
            # Create a radial gradient
            gradient = QConicalGradient(self.width() / 2, self.height() / 2, self.width() / 2)
            gradient.setColorAt(0, QColor(255, 0, 0))  # Center color (white)
            gradient.setColorAt(1, QColor(255, 0, 0))  # Outer color (transparent)

            # Set up the rainbow colors
            colors = [
                QColor(255, 127, 0),  # Orange
                QColor(255, 255, 0),  # Yellow
                QColor(0, 255, 0),    # Green
                QColor(0, 0, 255),    # Blue
                QColor(75, 0, 130),   # Indigo
                QColor(148, 0, 211)    # Violet
            ]
            
            # Create a linear gradient for the rainbow effect
            for i, color in enumerate(colors):
                gradient.setColorAt((i + 1) / (len(colors) + 1), color)

            # Set the brush and draw the rectangle
            painter.setBrush(QBrush(gradient))
            painter.drawRect(self.rect())
        else:
            # If a color is set, use the default button behavior
            super().paintEvent(event)

class JCanvasContainer(QScrollArea):
    def __init__(self, canvas, color: str = '#0c0c0c'):
        super().__init__()
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setStyleSheet(f'background-color: {color};')
        self.layout = QVBoxLayout()
        self.layout.addWidget(canvas, alignment=Qt.AlignCenter)
        self.container.setLayout(self.layout)
        self.setWidget(self.container)

    def setBackgroundColor(self, color: str = '#0c0c0c'):
        self.container.setStyleSheet(f'background-color: {color}')

    def set_canvas(self, new_canvas):
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()
        self.layout.addWidget(new_canvas, alignment=Qt.AlignCenter)
