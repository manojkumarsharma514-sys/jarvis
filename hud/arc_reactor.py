# hud/arc_reactor.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
import math

class ArcReactor(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.angle = (self.angle + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        cx = rect.center().x()
        cy = rect.center().y()
        radius = rect.width() / 2

        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(0, 360, 8):
            alpha = 180 if (i + self.angle) % 60 < 30 else 60
            painter.setBrush(QColor(0, 255, 255, alpha))

            rad = math.radians(i + self.angle)
            x = cx + math.cos(rad) * radius * 0.85
            y = cy + math.sin(rad) * radius * 0.85

            painter.drawEllipse(int(x), int(y), 6, 6)
