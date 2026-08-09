import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QTimer, Qt

class ParticleField(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Make transparent & ignore mouse
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create initial particles
        self.particles = []
        for _ in range(80):
            self.particles.append(self._new_particle())

        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def _new_particle(self):
        return {
            "x": random.uniform(0, self.width() or 900),
            "y": random.uniform(0, self.height() or 600),
            "r": random.uniform(1.5, 3.5),
            "vx": random.uniform(-0.15, 0.15),
            "vy": random.uniform(-0.25, -0.05),
            "a": random.randint(40, 120),
        }

    def animate(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < 0 or p["x"] < 0 or p["x"] > self.width():
                p.update(self._new_particle())
                p["y"] = self.height()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for p in self.particles:
            painter.setBrush(QColor(0, 220, 255, p["a"]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(p["x"]), int(p["y"]), int(p["r"]), int(p["r"]))
