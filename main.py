from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Callable, List

from PyQt6.QtCore import QPoint, QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass
class HUDState:
    status: str = "IDLE"
    last_command: str = ""
    last_response: str = ""
    log_lines: List[str] = field(default_factory=lambda: ["JARVIS ONLINE", "Awaiting command..."])


class ArcReactor(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.phase = 0.0
        self.active = False
        self.setMinimumSize(360, 360)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(35)

    def _animate(self) -> None:
        self.phase = (self.phase + (0.05 if self.active else 0.015)) % (2 * math.pi)
        self.update()

    def set_active(self, active: bool) -> None:
        self.active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        rect = self.rect().adjusted(10, 10, -10, -10)
        cx = rect.center().x()
        cy = rect.center().y()
        outer_r = min(rect.width(), rect.height()) * 0.42

        # Outer glow ring
        for alpha in (28, 42, 65, 90):
            radius = outer_r + 18 + (math.sin(self.phase) * 7)
            painter.setBrush(QColor(0, 200, 255, alpha))
            painter.drawEllipse(QPoint(cx, cy), int(radius), int(radius))

        # Outer circular frame
        painter.setBrush(QColor("#081f2d"))
        painter.drawEllipse(QPoint(cx, cy), int(outer_r + 16), int(outer_r + 16))

        # Core ring
        painter.setPen(QPen(QColor("#7fe7ff"), 3))
        painter.setBrush(QColor("#071c27"))
        for angle in range(0, 360, 12):
            start = angle + self.phase * 80
            arc_r = outer_r - 14
            painter.drawArc(
                int(cx - arc_r), int(cy - arc_r), int(arc_r * 2), int(arc_r * 2),
                int(start * 16), int(18 * 16),
            )

        # Triangular reactor core from Iron Man style
        points = [
            QPoint(cx, cy - int(outer_r * 0.68)),
            QPoint(cx - int(outer_r * 0.64), cy + int(outer_r * 0.52)),
            QPoint(cx + int(outer_r * 0.64), cy + int(outer_r * 0.52)),
        ]
        glow = QColor(0, 220, 255, 180)
        painter.setPen(QPen(glow, 2))
        painter.setBrush(QColor(0, 180, 255, 130))
        painter.drawPolygon(points)

        inner = [
            QPoint(cx, cy - int(outer_r * 0.42)),
            QPoint(cx - int(outer_r * 0.38), cy + int(outer_r * 0.30)),
            QPoint(cx + int(outer_r * 0.38), cy + int(outer_r * 0.30)),
        ]
        painter.setPen(QPen(QColor("#dffcff"), 2))
        painter.setBrush(QColor("#0b3b4d"))
        painter.drawPolygon(inner)

        # Center core glow
        center_r = outer_r * 0.18
        painter.setPen(QPen(QColor("#c7fcff"), 2))
        painter.setBrush(QColor(0, 229, 255, 170))
        painter.drawEllipse(QPoint(cx, cy), int(center_r), int(center_r))

        # Label
        painter.setPen(QColor("#dcffff"))
        painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "JARVIS")


class HUDPanel(QFrame):
    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setStyleSheet(
            "QFrame#panel { background: rgba(4, 18, 30, 180); border: 1px solid #1e90c7; border-radius: 12px; }"
        )
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(10)

        self.title = QLabel(title)
        self.title.setStyleSheet("color:#7fe4ff; font-size:11px; letter-spacing:2px; font-weight:700;")
        self.layout.addWidget(self.title)


class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = HUDState()
        self.submit_callback: Callable[[str], None] | None = None
        self.setWindowTitle("JARVIS HUD")
        self.resize(1500, 900)
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(
            "QMainWindow { background: #030c13; color: #dffaff; }"
            "QLabel { color: #dffaff; }"
            "QLineEdit { color: #dffaff; }"
        )

        container = QWidget(self)
        container.setStyleSheet("background: transparent;")
        self.setCentralWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        topbar = QHBoxLayout()
        topbar.setContentsMargins(10, 0, 10, 0)
        self.system_label = QLabel("JARVIS SYSTEM")
        self.system_label.setStyleSheet("color:#8feeff; font-size:20px; font-weight:700; letter-spacing:4px;")
        topbar.addWidget(self.system_label)
        topbar.addStretch()
        self.status_flag = QLabel("● LOCAL AI ONLINE")
        self.status_flag.setStyleSheet("color:#7dffcc; font-size:14px; font-weight:700;")
        topbar.addWidget(self.status_flag)
        root.addLayout(topbar)

        middle = QHBoxLayout()
        middle.setSpacing(18)
        root.addLayout(middle, 1)

        left_col = QVBoxLayout()
        left_col.setSpacing(14)

        status_panel = HUDPanel("STATUS")
        self.status_label = QLabel("IDLE")
        self.status_label.setStyleSheet("color:#67e7ff; font-size:32px; font-weight:700;")
        status_panel.layout.addWidget(self.status_label)
        self.command_label = QLabel("COMMAND / none")
        self.command_label.setStyleSheet("color:#dffafc; font-size:15px;")
        self.response_label = QLabel("RESPONSE / none")
        self.response_label.setStyleSheet("color:#c4ffd8; font-size:15px;")
        status_panel.layout.addWidget(self.command_label)
        status_panel.layout.addWidget(self.response_label)
        left_col.addWidget(status_panel, 1)

        log_panel = HUDPanel("ACTIVITY STREAM")
        self.log_label = QLabel()
        self.log_label.setWordWrap(True)
        self.log_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_label.setStyleSheet(
            "background: rgba(7, 18, 28, 180); color:#9adfff; border:1px solid #1c6c8f; border-radius:10px; padding:12px; font-family:Consolas; font-size:13px;"
        )
        log_panel.layout.addWidget(self.log_label)
        left_col.addWidget(log_panel, 2)

        middle.addLayout(left_col, 1)

        center_col = QVBoxLayout()
        center_col.setSpacing(18)

        reactor_panel = QFrame()
        reactor_panel.setObjectName("reactor")
        reactor_panel.setStyleSheet(
            "QFrame#reactor { background: rgba(5, 18, 28, 180); border: 1px solid #1a7ca9; border-radius: 12px; }"
        )
        reactor_layout = QVBoxLayout(reactor_panel)
        reactor_layout.setContentsMargins(20, 20, 20, 24)
        reactor_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.core = ArcReactor()
        reactor_layout.addWidget(self.core, 1, Qt.AlignmentFlag.AlignCenter)
        center_col.addWidget(reactor_panel, 3)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command here...")
        self.command_input.setStyleSheet(
            "QLineEdit { background: rgba(5, 19, 28, 180); border: 1px solid #1aa8da; border-radius: 10px; padding: 12px 14px; font-size:15px; }"
        )
        self.execute_button = QPushButton("RUN")
        self.execute_button.setStyleSheet(
            "QPushButton { background: #0d6f9b; color:white; border:1px solid #4ed9ff; border-radius:10px; padding:12px 18px; font-weight:700; }"
        )
        self.execute_button.clicked.connect(self.submit_current_command)
        self.command_input.returnPressed.connect(self.submit_current_command)
        input_row.addWidget(self.command_input)
        input_row.addWidget(self.execute_button)
        center_col.addLayout(input_row)

        middle.addLayout(center_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(14)

        diag_panel = HUDPanel("SYSTEM DIAGNOSTICS")
        diag_panel.layout.addWidget(QLabel("CPU  34%"))
        diag_panel.layout.addWidget(QLabel("GPU  41%"))
        diag_panel.layout.addWidget(QLabel("MEM  58%"))
        diag_panel.layout.addWidget(QLabel("NET  ONLINE"))
        right_col.addWidget(diag_panel, 1)

        weather_panel = HUDPanel("ENVIRONMENT")
        weather_panel.layout.addWidget(QLabel("TEMP: 30°C"))
        weather_panel.layout.addWidget(QLabel("HUMIDITY: 14%"))
        weather_panel.layout.addWidget(QLabel("WEATHER: CLEAR"))
        weather_panel.layout.addWidget(QLabel("LOCAL TIME: 05:15:21"))
        right_col.addWidget(weather_panel, 1)

        middle.addLayout(right_col, 0.7)

        self.update_ui()

    def set_submit_callback(self, callback) -> None:
        self.submit_callback = callback

    def submit_current_command(self) -> None:
        if self.submit_callback is None:
            return
        text = self.command_input.text().strip()
        self.command_input.clear()
        if text:
            self.submit_callback(text)

    def update_ui(self) -> None:
        self.status_label.setText(self.state.status)
        self.command_label.setText(f"COMMAND / {self.state.last_command or 'none'}")
        self.response_label.setText(f"RESPONSE / {self.state.last_response or 'none'}")
        self.log_label.setText("\n".join(self.state.log_lines[-12:]))
        self.core.set_active(self.state.status in {"THINKING", "SPEAKING", "VISION", "LISTENING"})

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
