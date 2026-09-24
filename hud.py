from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import List

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget


@dataclass
class HUDState:
    status: str = "IDLE"
    last_command: str = ""
    last_response: str = ""
    log_lines: List[str] = field(default_factory=lambda: ["JARVIS ONLINE", "Awaiting command..."])


class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = HUDState()
        self.setWindowTitle("JARVIS HUD")
        self.resize(1200, 720)
        self.setStyleSheet("background: #060d17; color: white;")

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        self.status_label = QLabel("IDLE", self.central)
        self.status_label.setStyleSheet("color: #6ee7ff; font-size: 26px; font-weight: bold;")
        self.status_label.move(40, 30)

        self.command_label = QLabel("Last command: none", self.central)
        self.command_label.setStyleSheet("color: #dff7ff; font-size: 16px;")
        self.command_label.move(40, 80)

        self.response_label = QLabel("Last response: none", self.central)
        self.response_label.setStyleSheet("color: #b5ffd9; font-size: 16px;")
        self.response_label.move(40, 120)

        self.log_label = QLabel(self.central)
        self.log_label.setStyleSheet("color: #8fe6ff; font-size: 14px; background: rgba(15,30,45,0.9); border: 1px solid #0bb7ff; border-radius: 10px; padding: 12px;")
        self.log_label.setWordWrap(True)
        self.log_label.resize(500, 250)
        self.log_label.move(40, 170)

        self.ai_ring = QLabel("AI", self.central)
        self.ai_ring.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ai_ring.setStyleSheet(
            "background: radial-gradient(circle, #0ff 0%, #0aa 20%, #070d16 70%); "
            "border: 2px solid #6ee7ff; border-radius: 100px; color: black; "
            "font-size: 22px; font-weight: bold;"
        )
        self.ai_ring.resize(180, 180)
        self.ai_ring.move(760, 120)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.animate_status)
        self.status_timer.start(250)

        self.update_ui()

    def animate_status(self):
        if self.state.status == "THINKING":
            self.ai_ring.setText("AI")
            self.ai_ring.setStyleSheet(
                "background: radial-gradient(circle, #7ef9ff 0%, #00b7ff 25%, #0a2436 70%); "
                "border: 2px solid #d8ffff; border-radius: 100px; color: black; "
                "font-size: 22px; font-weight: bold;"
            )
        else:
            self.ai_ring.setStyleSheet(
                "background: radial-gradient(circle, #0ff 0%, #0aa 20%, #070d16 70%); "
                "border: 2px solid #6ee7ff; border-radius: 100px; color: black; "
                "font-size: 22px; font-weight: bold;"
            )

    def update_ui(self):
        self.status_label.setText(self.state.status)
        self.command_label.setText(f"Last command: {self.state.last_command or 'none'}")
        self.response_label.setText(f"Last response: {self.state.last_response or 'none'}")
        log_text = "\n".join(self.state.log_lines[-8:])
        self.log_label.setText(log_text)

    def append_log(self, message: str):
        self.state.log_lines.append(message)
        if len(self.state.log_lines) > 20:
            self.state.log_lines = self.state.log_lines[-20:]
        self.update_ui()

    def update_status(self, status: str, command: str = "", response: str = ""):
        self.state.status = status.upper()
        if command:
            self.state.last_command = command
        if response:
            self.state.last_response = response
        self.update_ui()


def start_hud():
    app = QApplication.instance() or QApplication(sys.argv)
    window = JarvisHUD()
    window.show()
    return app, window


if __name__ == "__main__":
    app, window = start_hud()
    sys.exit(app.exec())
