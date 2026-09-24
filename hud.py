from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import List

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


@dataclass
class HUDState:
    status: str = "IDLE"
    last_command: str = ""
    last_response: str = ""
    log_lines: List[str] = field(
        default_factory=lambda: ["JARVIS ONLINE", "Awaiting command..."]
    )


class ArcReactor(QWidget):
    """Animated JARVIS-style core drawn with Qt, without image assets."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.phase = 0.0
        self.active = False
        self.setMinimumSize(260, 260)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(40)

    def _animate(self) -> None:
        self.phase = (self.phase + (0.035 if self.active else 0.012)) % (2 * math.pi)
        self.update()

    def set_active(self, active: bool) -> None:
        self.active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        center = self.rect().center()
        radius = min(self.width(), self.height()) * 0.37
        pulse = math.sin(self.phase) * (5 if self.active else 2)

        # Soft glow layers.
        for index, alpha in enumerate((18, 28, 42, 65)):
            glow_radius = radius + 34 - index * 7 + pulse
            painter.setBrush(QColor(0, 190, 255, alpha))
            painter.drawEllipse(center, int(glow_radius), int(glow_radius))

        painter.setBrush(QColor("#061923"))
        painter.drawEllipse(center, int(radius), int(radius))

        # Rotating technical arcs.
        for offset, span, width in ((self.phase * 40, 105, 3), (-self.phase * 25, 55, 2), (20, 25, 4)):
            pen = QPen(QColor("#66e8ff"), width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(
                int(center.x() - radius - 11),
                int(center.y() - radius - 11),
                int((radius + 11) * 2),
                int((radius + 11) * 2),
                int((offset % 360) * 16),
                int(span * 16),
            )

        painter.setPen(QPen(QColor("#a9f7ff"), 2))
        painter.setBrush(QColor("#11b9e8"))
        painter.drawEllipse(center, int(radius * 0.46), int(radius * 0.46))
        painter.setBrush(QColor("#062331"))
        painter.drawEllipse(center, int(radius * 0.31), int(radius * 0.31))

        painter.setPen(QColor("#d9fbff"))
        painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "JARVIS")


class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = HUDState()
        self.setWindowTitle("JARVIS HUD")
        self.resize(1280, 760)
        self.setMinimumSize(1000, 620)
        self.setStyleSheet("QMainWindow { background: #020a12; color: #dffaff; }")

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        title = QLabel("J.A.R.V.I.S")
        title.setStyleSheet("color:#8feeff; font-size:30px; font-weight:700; letter-spacing:4px;")
        header.addWidget(title)
        header.addStretch()
        self.connection_label = QLabel("● LOCAL AI ONLINE")
        self.connection_label.setStyleSheet("color:#7dffcc; font-size:14px; font-weight:600;")
        header.addWidget(self.connection_label)
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(22)
        root.addLayout(content, 1)

        left = QFrame()
        left.setObjectName("panel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(24, 22, 24, 22)
        left_layout.setSpacing(14)

        self.status_label = QLabel("IDLE")
        self.status_label.setStyleSheet("color:#68e5ff; font-size:34px; font-weight:700;")
        left_layout.addWidget(self.status_label)

        self.command_label = QLabel("COMMAND  /  none")
        self.response_label = QLabel("RESPONSE  /  none")
        for label, color in ((self.command_label, "#dff7ff"), (self.response_label, "#a9ffd8")):
            label.setStyleSheet(f"color:{color}; font-size:15px;")
            label.setWordWrap(True)
            left_layout.addWidget(label)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color:#164c61;")
        left_layout.addWidget(divider)

        log_title = QLabel("ACTIVITY STREAM")
        log_title.setStyleSheet("color:#4fcce9; font-size:12px; font-weight:700; letter-spacing:2px;")
        left_layout.addWidget(log_title)

        self.log_label = QLabel()
        self.log_label.setWordWrap(True)
        self.log_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_label.setStyleSheet(
            "color:#8fe6ff; background:#061722; border:1px solid #12617b; "
            "border-radius:10px; padding:16px; font-family:Consolas; font-size:14px;"
        )
        left_layout.addWidget(self.log_label, 1)
        content.addWidget(left, 5)

        right = QFrame()
        right.setObjectName("corePanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.core = ArcReactor()
        right_layout.addWidget(self.core, 1, Qt.AlignmentFlag.AlignCenter)
        core_caption = QLabel("NEURAL CORE  /  READY")
        core_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        core_caption.setStyleSheet("color:#65d9f5; font-size:12px; letter-spacing:2px;")
        right_layout.addWidget(core_caption)
        content.addWidget(right, 4)

        central.setStyleSheet(
            "QFrame#panel, QFrame#corePanel { background:#071521; border:1px solid #16738e; border-radius:14px; }"
        )

        self.update_ui()

    def update_ui(self) -> None:
        self.status_label.setText(self.state.status)
        self.command_label.setText(f"COMMAND  /  {self.state.last_command or 'none'}")
        self.response_label.setText(f"RESPONSE  /  {self.state.last_response or 'none'}")
        self.log_label.setText("\n".join(self.state.log_lines[-10:]))
        self.core.set_active(self.state.status in {"THINKING", "SPEAKING", "VISION"})

    def append_log(self, message: str) -> None:
        self.state.log_lines.append(message)
        self.state.log_lines = self.state.log_lines[-20:]
        self.update_ui()

    def update_status(self, status: str, command: str = "", response: str = "") -> None:
        self.state.status = status.upper()
        if command:
            self.state.last_command = command
        if response:
            self.state.last_response = response
        self.append_log(f"[{self.state.status}] {command or response or 'ready'}")


def start_hud():
    app = QApplication.instance() or QApplication(sys.argv)
    window = JarvisHUD()
    window.show()
    app.processEvents()
    return app, window


if __name__ == "__main__":
    app, window = start_hud()
    sys.exit(app.exec())
