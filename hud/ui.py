from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QPointF
import random, math

# ------------------------
# Glass Panel Widget (draggable within HUD)
# ------------------------
class GlassPanel(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.dragging = False
        self.drag_offset = QPointF(0, 0)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.setBrush(QColor(10, 30, 40, 160))
        painter.setPen(QColor(0, 255, 255, 120))
        painter.drawRoundedRect(rect, 18, 18)
        if self.title:
            painter.setPen(QColor(0, 255, 255))
            painter.setFont(QFont("Consolas", 11))
            painter.drawText(
                rect.adjusted(4, 4, -4, -4),
                Qt.AlignmentFlag.AlignCenter,
                self.title,
            )

    # ---------------- Mouse Dragging ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.position()

    def mouseMoveEvent(self, event):
        if self.dragging and self.parent():
            new_pos = self.mapToParent(event.position() - self.drag_offset)
            new_x = max(0, min(self.parent().width() - self.width(), int(new_pos.x())))
            new_y = max(0, min(self.parent().height() - self.height(), int(new_pos.y())))
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        self.dragging = False


# ------------------------
# Chat / Command Panel (FIXED – NOT DRAGGABLE)
# ------------------------
class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.setMinimumHeight(140)

    def add_message(self, sender, text):
        self.messages.append((sender, text))
        if len(self.messages) > 5:
            self.messages.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(6, 6, -6, -6)
        painter.setBrush(QColor(10, 30, 40, 160))
        painter.setPen(QColor(0, 255, 255, 120))
        painter.drawRoundedRect(rect, 16, 16)
        painter.setFont(QFont("Consolas", 10))
        y = rect.top() + 12
        for sender, text in self.messages:
            if sender == "USER":
                painter.setPen(QColor(0, 200, 255))
                label = "USER > "
            else:
                painter.setPen(QColor(0, 255, 180))
                label = "JARVIS > "
            painter.drawText(rect.left() + 12, y, label + text)
            y += 22

    # Disable dragging
    def mousePressEvent(self, event): event.ignore()
    def mouseMoveEvent(self, event): event.ignore()
    def mouseReleaseEvent(self, event): event.ignore()


# ------------------------
# AI Agent Widget
# ------------------------
class AIAgent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pulse = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        self.pulse += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        center = QPointF(w / 2, h / 2)
        radius = 60 + 10 * math.sin(self.pulse)
        painter.setBrush(QColor(0, 255, 255, 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius, radius)
        painter.setBrush(QColor(0, 200, 255))
        painter.drawEllipse(center, 40, 40)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Consolas", 12))
        painter.drawText(int(center.x() - 15), int(center.y() + 5), "AI")


# ------------------------
# HUD MAIN
# ------------------------
class HUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS HUD")
        self.resize(1400, 800)
        self.setStyleSheet("background-color: #050b10;")

        # Layout constants (ADDED)
        self.chat_height = 130
        self.chat_margin = 40
        self.panel_gap = 20

        # Grid animation
        self.grid_offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

        # Status text
        self.status_text = "JARVIS ONLINE"
        self.status_index = 0
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.animate_status)
        self.status_timer.start(100)

        # Particles
        self.particles = []
        for _ in range(80):
            self.particles.append({
                'pos': QPointF(random.randint(0, self.width()), random.randint(0, self.height())),
                'radius': random.randint(2, 4),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'alpha': random.randint(60, 150)
            })

        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self.animate_particles)
        self.particle_timer.start(50)

        # Center AI
        self.ai_agent = AIAgent(self)
        self.ai_agent.setFixedSize(200, 200)
        self.ai_agent.move(self.width() // 2 - 100, self.height() // 2 - 100)

        # CPU / RAM
        self.cpu = GlassPanel("CPU", self)
        self.cpu.setFixedSize(80, 80)
        self.ram = GlassPanel("RAM", self)
        self.ram.setFixedSize(80, 80)

        # NET / SYS
        self.net = GlassPanel("NET", self)
        self.net.setFixedSize(80, 80)
        self.sys = GlassPanel("SYS", self)
        self.sys.setFixedSize(80, 80)

        # Chat panel (TOP)
        self.chat_panel = ChatPanel(self)
        self.chat_panel.setGeometry(
            self.chat_margin,
            self.chat_margin,
            self.width() - self.chat_margin * 2,
            self.chat_height
        )

        # Overlay panels
        self.left_panel = GlassPanel("AI MODULE", self)
        self.right_panel = GlassPanel("SYSTEM STATUS", self)
        self.bottom_panel = GlassPanel("COMMAND STREAM", self)

        self._position_panels()

        # Initial messages
        self.add_chat("JARVIS", "HUD initialized")
        self.add_chat("USER", "Awaiting command")

    def add_chat(self, sender, text):
        self.chat_panel.add_message(sender, text)

    def _position_panels(self):
        w, h = self.width(), self.height()
        chat_bottom = self.chat_margin + self.chat_height

        self.left_panel.setGeometry(
            20,
            chat_bottom + self.panel_gap,
            260,
            h - (chat_bottom + self.panel_gap) - 60
        )

        self.right_panel.setGeometry(
            w - 280,
            chat_bottom + self.panel_gap,
            260,
            h - (chat_bottom + self.panel_gap) - 60
        )

        self.bottom_panel.setGeometry(
            320,
            h - 180,
            w - 640,
            140
        )

        self.chat_panel.raise_()
        self.left_panel.raise_()
        self.right_panel.raise_()
        self.bottom_panel.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.chat_panel.setGeometry(
            self.chat_margin,
            self.chat_margin,
            self.width() - self.chat_margin * 2,
            self.chat_height
        )

        self._position_panels()

        # CPU / RAM (left bottom)
        self.cpu.move(330, self.height() - 300)
        self.ram.move(420, self.height() - 300)

        # NET / SYS (right bottom)
        self.sys.move(self.width() - 490, self.height() - 300)
        self.net.move(self.width() - 400, self.height() - 300)

    # ---------------- Animations ----------------
    def animate(self):
        self.grid_offset = (self.grid_offset + 1) % 40
        self.update()

    def animate_status(self):
        self.status_index = (self.status_index + 1) % (len(self.status_text) + 1)
        self.update()

    def animate_particles(self):
        for p in self.particles:
            p['pos'].setX(p['pos'].x() + p['dx'])
            p['pos'].setY(p['pos'].y() + p['dy'])
            if p['pos'].x() < 0: p['pos'].setX(self.width())
            if p['pos'].x() > self.width(): p['pos'].setX(0)
            if p['pos'].y() < 0: p['pos'].setY(self.height())
            if p['pos'].y() > self.height(): p['pos'].setY(0)
        self.update()

    def update_status(self, text):
        self.status_text = text
        self.status_index = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Grid
        painter.setPen(QColor(0, 60, 80, 80))
        step = 40
        for x in range(-step, self.width(), step):
            painter.drawLine(x + self.grid_offset, 0, x + self.grid_offset, self.height())
        for y in range(-step, self.height(), step):
            painter.drawLine(0, y + self.grid_offset, self.width(), y + self.grid_offset)

        # Status text
        painter.setFont(QFont("Consolas", 16))
        rect = self.rect()
        text = self.status_text[:self.status_index]
        painter.setPen(QColor(0, 255, 255, 80))
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            painter.drawText(rect.translated(dx, dy),
                             Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                             text)
        painter.setPen(QColor(0, 255, 255))
        painter.drawText(rect,
                         Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                         text)

        # Particles
        for p in self.particles:
            painter.setBrush(QColor(0, 255, 255, p['alpha']))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(p['pos'], p['radius'], p['radius'])
