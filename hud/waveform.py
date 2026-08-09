# hud/waveform.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
import math
import random
from hud.audio_input import audio_input

class WaveformRing(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.phase += 0.15
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        radius = min(w, h) // 2 - 15

        level = min(audio_input.read_level() * 4, 1.5)

        painter.setPen(QColor(0, 255, 255))

        for i in range(120):
            angle = (i / 120) * 2 * math.pi
            wave = math.sin(angle * 6 + self.phase) * 12 * level

            x1 = cx + math.cos(angle) * radius
            y1 = cy + math.sin(angle) * radius
            x2 = cx + math.cos(angle) * (radius + wave)
            y2 = cy + math.sin(angle) * (radius + wave)

            # ✅ FORCE INT
            painter.drawLine(
                int(x1), int(y1),
                int(x2), int(y2)
            )
