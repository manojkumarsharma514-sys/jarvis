from __future__ import annotations

import sys
from typing import List

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget


class CinematicHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS HUD")
        self.resize(1280, 760)
        self.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #020b14, stop:1 #071d2d);")

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        self.status = QLabel("SYSTEM ONLINE", self.central)
        self.status.setStyleSheet("font-size: 28px; font-weight: bold; color: #7be7ff; margin: 20px;")
        self.status.move(50, 30)

        self.chat = QLabel("JARVIS READY\nAwaiting command...", self.central)
        self.chat.setStyleSheet("font-size: 18px; color: #d5f7ff; background: rgba(12, 32, 46, 180); border: 1px solid #5fe8ff; border-radius: 12px; padding: 18px;")
        self.chat.resize(520, 220)
        self.chat.move(50, 110)

        self.ai_core = QLabel("AI", self.central)
        self.ai_core.setStyleSheet("font-size: 26px; font-weight: bold; color: #02151d; background: radial-gradient(circle, #7af7ff 0%, #1cd3ff 30%, #0d1f30 75%); border: 2px solid #8ceeff; border-radius: 120px;")
        self.ai_core.resize(240, 240)
        self.ai_core.move(900, 160)
        self.ai_core.setAlignment(__import__('PyQt6.QtCore').Qt.AlignmentFlag.AlignCenter)

        self.log = QLabel("[BOOT]\nJARVIS initialized\n[OK] Safety online\n[OK] Memory ready\n[WAIT] Listening for command...", self.central)
        self.log.setStyleSheet("font-size: 15px; color: #99ebff; background: rgba(15, 24, 30, 180); border: 1px solid #2ad5ff; border-radius: 10px; padding: 10px;")
        self.log.resize(500, 220)
        self.log.move(50, 380)

        self.ring1 = QLabel("CPU", self.central)
        self.ring1.setStyleSheet("font-size: 14px; color: #9ef9ff; background: rgba(11,30,38,180); border: 2px solid #54daff; border-radius: 80px;")
        self.ring1.resize(140, 140)
        self.ring1.move(700, 500)
        self.ring1.setAlignment(__import__('PyQt6.QtCore').Qt.AlignmentFlag.AlignCenter)

        self.ring2 = QLabel("RAM", self.central)
        self.ring2.setStyleSheet("font-size: 14px; color: #9ef9ff; background: rgba(11,30,38,180); border: 2px solid #54daff; border-radius: 80px;")
        self.ring2.resize(140, 140)
        self.ring2.move(860, 500)
        self.ring2.setAlignment(__import__('PyQt6.QtCore').Qt.AlignmentFlag.AlignCenter)

        self.ring3 = QLabel("NET", self.central)
        self.ring3.setStyleSheet("font-size: 14px; color: #9ef9ff; background: rgba(11,30,38,180); border: 2px solid #54daff; border-radius: 80px;")
        self.ring3.resize(140, 140)
        self.ring3.move(1020, 500)
        self.ring3.setAlignment(__import__('PyQt6.QtCore').Qt.AlignmentFlag.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(250)

    def animate(self):
        self.ai_core.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #02151d; "
            "background: radial-gradient(circle, #d7fdff 0%, #61ebff 20%, #0d1f30 75%); "
            "border: 2px solid #8ceeff; border-radius: 120px;"
        )
        self.status.setText("SYSTEM ONLINE")


def show_cinematic_hud():
    app = QApplication.instance() or QApplication(sys.argv)
    window = CinematicHUD()
    window.show()
    return app, window


if __name__ == "__main__":
    app, window = show_cinematic_hud()
    sys.exit(app.exec())
