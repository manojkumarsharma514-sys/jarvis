from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer
import psutil
import math
import random


class CircularRing(QWidget):
    def __init__(self, label="CPU", parent=None):
        super().__init__(parent)
        self.label = label
        self.value = 0
        self.angle = 0
        self.pulse = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(500)  # update system stats every 0.5s

    def update_stats(self):
        # Real system values
        if self.label == "CPU":
            self.value = psutil.cpu_percent()
        elif self.label == "RAM":
            self.value = psutil.virtual_memory().percent
        elif self.label == "NET":
            net = psutil.net_io_counters()
            self.value = (net.bytes_sent + net.bytes_recv) % 100
        elif self.label == "SYS":
            self.value = psutil.disk_usage("/").percent

        self.angle = (self.angle + 2) % 360
        self.pulse = (self.pulse + 1) % 360
        self.update()

    def draw_glow(self, painter, rect, color, steps=6, max_radius=10):
        for i in range(steps):
            alpha = int(50 / (i + 1))
            glow_color = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setBrush(glow_color)
            painter.setPen(Qt.PenStyle.NoPen)
            margin = int(max_radius * i / steps)
            painter.drawEllipse(rect.adjusted(-margin, -margin, margin, margin))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2

        # Pulsing factor based on value
        pulse_radius = radius + int(3 * math.sin(math.radians(self.pulse)))

        # Background ring
        pen = QPen(QColor(0, 80, 100))
        pen.setWidth(6)
        painter.setPen(pen)
        painter.drawEllipse(center, pulse_radius, pulse_radius)

        # Active arc
        pen.setColor(QColor(0, 255, 255))
        painter.setPen(pen)
        span = int(-self.value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, span)

        # Rotating sweep
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawArc(rect, self.angle * 16, 40 * 16)

        # Glow
        self.draw_glow(painter, rect, QColor(0, 255, 255), steps=4, max_radius=8)

        # Label + Value
        painter.setPen(QColor(0, 200, 255))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.label}\n{int(self.value)}%"
        )
