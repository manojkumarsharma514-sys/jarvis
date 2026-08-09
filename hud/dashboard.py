import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


# ------------------ Glass Panel ------------------
class GlassPanel(QFrame):
    def __init__(self, title=""):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 30, 50, 180);
                border-radius: 14px;
                border: 1px solid rgba(0, 180, 255, 120);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        if title:
            label = QLabel(title)
            label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            label.setStyleSheet("color: #00c8ff;")
            layout.addWidget(label)

        self.body = QVBoxLayout()
        layout.addLayout(self.body)


# ------------------ Main Dashboard ------------------
class JarvisDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS AI DASHBOARD")
        self.setMinimumSize(1200, 720)
        self.setStyleSheet("background-color: #0b1220;")

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)

        # ---------- TOP BAR ----------
        top_bar = QHBoxLayout()

        title = QLabel("JARVIS")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #00d4ff;")

        search = QLineEdit()
        search.setPlaceholderText("Search command, file, task...")
        search.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,40);
                color: white;
                padding: 8px;
                border-radius: 10px;
            }
        """)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(search)

        main_layout.addLayout(top_bar)

        # ---------- GRID ----------
        grid = QGridLayout()
        grid.setSpacing(12)

        # LEFT PANEL
        left_panel = GlassPanel("AI Modules")
        left_panel.body.addWidget(QLabel("• Chat Agent"))
        left_panel.body.addWidget(QLabel("• File Manager"))
        left_panel.body.addWidget(QLabel("• System Control"))
        left_panel.body.addWidget(QLabel("• Automation"))
        grid.addWidget(left_panel, 0, 0, 2, 1)

        # CENTER PANEL
        center_panel = GlassPanel("AI AGENT")
        ai_icon = QLabel("🤖")
        ai_icon.setFont(QFont("Segoe UI Emoji", 48))
        ai_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status = QLabel("Status: ONLINE\nAwaiting command...")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet("color: #d0f0ff;")

        center_panel.body.addWidget(ai_icon)
        center_panel.body.addWidget(status)
        grid.addWidget(center_panel, 0, 1, 1, 2)

        # LOG PANEL
        log_panel = GlassPanel("SYSTEM LOGS")
        logs = QTextEdit()
        logs.setReadOnly(True)
        logs.setText(
            "[BOOT] JARVIS initialized\n"
            "[OK] Core systems online\n"
            "[WAIT] Listening for command..."
        )
        logs.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,120);
                color: #00ffcc;
                border-radius: 8px;
            }
        """)
        log_panel.body.addWidget(logs)
        grid.addWidget(log_panel, 1, 1, 1, 2)

        # STATS PANEL
        stats_panel = GlassPanel("SYSTEM STATUS")
        stats_panel.body.addWidget(QLabel("CPU: 42%"))
        stats_panel.body.addWidget(QLabel("RAM: 58%"))
        stats_panel.body.addWidget(QLabel("NET: Stable"))
        grid.addWidget(stats_panel, 2, 0, 1, 1)

        # CHART PANEL
        chart_panel = GlassPanel("ACTIVITY")
        chart_panel.body.addWidget(QLabel("Usage graphs coming soon"))
        grid.addWidget(chart_panel, 2, 1, 1, 2)

        main_layout.addLayout(grid)


# ------------------ RUN ------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisDashboard()
    window.show()
    sys.exit(app.exec())
