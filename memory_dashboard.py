from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QTextEdit, QVBoxLayout, QWidget

from memory import Memory


class MemoryDashboard(QMainWindow):
    def __init__(self, memory: Optional[Memory] = None):
        super().__init__()
        self.memory = memory or Memory()
        self.setWindowTitle("JARVIS Memory Dashboard")
        self.resize(900, 700)

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("JARVIS MEMORY")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #67e8f9;")
        layout.addWidget(title)

        memory_text = QTextEdit()
        memory_text.setReadOnly(True)
        memory_text.setStyleSheet("background: #091827; color: #d9f8ff; font-size: 13px;")

        rows = self.memory.all_memory()
        if rows:
            content = []
            for key, value, updated_at in rows:
                content.append(f"[{updated_at}] {key}: {value}")
            memory_text.setText("\n".join(content))
        else:
            memory_text.setText("No saved memory yet.")

        layout.addWidget(memory_text)
        self.setCentralWidget(central)


def show_memory_dashboard() -> MemoryDashboard:
    app = QApplication.instance() or QApplication(sys.argv)
    win = MemoryDashboard()
    win.show()
    return win


if __name__ == "__main__":
    show_memory_dashboard()
    sys.exit(QApplication.instance().exec())
