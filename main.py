#!/usr/bin/env python3
"""
Civic e:HEV (FL4) Cyberpunk OBD2 Dashboard
Main Entry Point
"""

import sys
import os
import argparse

# Ensure local site-packages is in sys.path if present
local_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site-packages")
if os.path.exists(local_site) and local_site not in sys.path:
    sys.path.insert(0, local_site)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QColor, QPalette, QKeyEvent
from PyQt5.QtCore import Qt, QTimer

from core.telemetry import VehicleTelemetry
from core.mock_simulator import MockSimulator
from core.obd_reader import OBDReader
from widgets.header_footer import HeaderWidget, FooterWidget
from widgets.battery_monitor import BatteryMonitorWidget
from widgets.speed_power_gauge import SpeedPowerGaugeWidget
from widgets.telemetry_panel import TelemetryPanelWidget
from themes.cyberpunk_theme import CyberTheme
from themes.eva_theme import EvaTheme


class CockpitCentralWidget(QWidget):
    """Cockpit HUD background with full-screen theme framing & perimeter brackets."""
    def __init__(self, parent=None, theme="eva"):
        super().__init__(parent)
        self.theme = theme

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen
        from PyQt5.QtCore import QRectF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        W, H = self.width(), self.height()
        is_eva = self.theme == "eva"

        # Fill base background & pattern
        if is_eva:
            painter.fillRect(0, 0, W, H, EvaTheme.BG_DARK)
            # Subtle Eva tactical framing
            pen_border = QPen(EvaTheme.GRID_LINE_BRIGHT, 1.2)
            painter.setPen(pen_border)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(2, 2, W - 4, H - 4)

            # NERV Orange Accent Brackets & Corner Hazard Tape Blocks
            c_len = 24
            pen_corner = QPen(EvaTheme.NERV_ORANGE, 2.2)
            painter.setPen(pen_corner)
            painter.drawLine(2, 2 + c_len, 2, 2)
            painter.drawLine(2, 2, 2 + c_len, 2)
            painter.drawLine(W - 2 - c_len, 2, W - 2, 2)
            painter.drawLine(W - 2, 2, W - 2, 2 + c_len)
            painter.drawLine(2, H - 2 - c_len, 2, H - 2)
            painter.drawLine(2, H - 2, 2 + c_len, H - 2)
            painter.drawLine(W - 2 - c_len, H - 2, W - 2, H - 2)
            painter.drawLine(W - 2, H - 2, W - 2, H - 2 - c_len)

            # Sleek Eva Tactical Edge Bezel Framing
            pen_inner = QPen(QColor(180, 80, 255, 60), 1.0)
            painter.setPen(pen_inner)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(6, 6, W - 12, H - 12)
        else:
            painter.fillRect(0, 0, W, H, CyberTheme.BG_DARK)
            CyberTheme.draw_carbon_pattern(painter, QRectF(0, 0, W, H))

            # Viewport Outer Perimeter Framing
            pen_border = QPen(CyberTheme.GRID_LINE_BRIGHT, 1.2)
            painter.setPen(pen_border)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(2, 2, W - 4, H - 4)

            # 4 Corner Accent Cyber Brackets
            c_len = 24
            pen_corner = QPen(CyberTheme.CYAN_DIM, 2.0)
            painter.setPen(pen_corner)
            painter.drawLine(2, 2 + c_len, 2, 2)
            painter.drawLine(2, 2, 2 + c_len, 2)
            painter.drawLine(W - 2 - c_len, 2, W - 2, 2)
            painter.drawLine(W - 2, 2, W - 2, 2 + c_len)
            painter.drawLine(2, H - 2 - c_len, 2, H - 2)
            painter.drawLine(2, H - 2, 2 + c_len, H - 2)
            painter.drawLine(W - 2 - c_len, H - 2, W - 2, H - 2)
            painter.drawLine(W - 2, H - 2, W - 2, H - 2 - c_len)


class CivicDashboardWindow(QMainWindow):
    def __init__(self, port="/dev/ttyUSB0", force_mock=False, fullscreen=False, width=1280, height=720, theme="eva"):
        super().__init__()
        self.theme = theme
        self.update_window_title()
        self.resize(width, height)

        # Apply dark window background
        palette = QPalette()
        palette.setColor(QPalette.Window, EvaTheme.BG_DARK if self.theme == "eva" else CyberTheme.BG_DARK)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Central Layout Container with custom graphics
        self.central_widget = CockpitCentralWidget(self, theme=self.theme)
        self.setCentralWidget(self.central_widget)
        main_vbox = QVBoxLayout(self.central_widget)
        main_vbox.setContentsMargins(10, 6, 10, 6)
        main_vbox.setSpacing(6)

        # 1. Top Header
        self.header = HeaderWidget(self, theme=self.theme)
        self.header.setFixedHeight(45)
        main_vbox.addWidget(self.header)

        # 2. Main Middle Dashboard Area (3 Columns: Battery | Center Dial | Telemetry)
        mid_hbox = QHBoxLayout()
        mid_hbox.setSpacing(12)

        # Left Column: Hybrid Battery Monitor & Particle Flow / 2D Avatar
        self.battery_panel = BatteryMonitorWidget(self, theme=self.theme)
        self.battery_panel.setMinimumWidth(340)
        mid_hbox.addWidget(self.battery_panel, stretch=3)

        # Center Column: Speed, Power/Charge & A.T. Field G-Force Dial
        self.center_dial = SpeedPowerGaugeWidget(self, theme=self.theme)
        self.center_dial.setMinimumWidth(400)
        mid_hbox.addWidget(self.center_dial, stretch=4)

        # Right Column: Engine, 12V Aux, Throttle & Motor Power
        self.telemetry_panel = TelemetryPanelWidget(self, theme=self.theme)
        self.telemetry_panel.setMinimumWidth(320)
        mid_hbox.addWidget(self.telemetry_panel, stretch=3)

        main_vbox.addLayout(mid_hbox, stretch=1)

        # 3. Bottom Footer
        self.footer = FooterWidget(self, theme=self.theme)
        self.footer.setFixedHeight(35)
        main_vbox.addWidget(self.footer)

        # 4. Telemetry Source (OBDReader or MockSimulator)
        self.port = port
        self.force_mock = force_mock
        self.reader_thread = None
        self.telemetry = VehicleTelemetry()
        self.init_telemetry_source()

        # 5. 60 FPS Render Loop Timer (~16ms)
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self.on_render_tick)
        self.render_timer.start(16)

        if fullscreen:
            self.showFullScreen()
        else:
            self.show()

    def update_window_title(self):
        if self.theme == "eva":
            self.setWindowTitle("Honda Civic e:HEV (FL4) - EVA NERV 綾波零 Cockpit HUD [Press 'T' to Toggle Theme]")
        else:
            self.setWindowTitle("Honda Civic e:HEV (FL4) - Cyberpunk Race Queen Dashboard [Press 'T' to Toggle Theme]")

    def toggle_theme(self):
        """Switches between EVA NERV theme and Cyberpunk theme seamlessly."""
        self.theme = "cyberpunk" if self.theme == "eva" else "eva"
        print(f"[CivicDashboard] Switched theme to: {self.theme.upper()}")
        self.update_window_title()

        palette = QPalette()
        palette.setColor(QPalette.Window, EvaTheme.BG_DARK if self.theme == "eva" else CyberTheme.BG_DARK)
        self.setPalette(palette)

        self.central_widget.set_theme(self.theme)
        self.header.set_theme(self.theme)
        self.battery_panel.set_theme(self.theme)
        self.center_dial.set_theme(self.theme)
        self.telemetry_panel.set_theme(self.theme)
        self.footer.set_theme(self.theme)

    def init_telemetry_source(self):
        """Initializes hardware OBD reader or falls back automatically to mock simulator."""
        if self.reader_thread:
            self.reader_thread.stop()

        # Check if physical port exists
        has_port = os.path.exists(self.port)

        if not self.force_mock and has_port:
            print(f"[CivicDashboard] Connecting to physical OBD2 port: {self.port}")
            self.reader_thread = OBDReader(port=self.port, baudrate=115200)
        else:
            reason = "Force Mock specified" if self.force_mock else f"Port '{self.port}' not found"
            print(f"[CivicDashboard] Auto-starting Mock Simulator ({reason})")
            self.reader_thread = MockSimulator()

        self.reader_thread.telemetry_updated.connect(self.on_telemetry_updated)
        self.reader_thread.start()

    def on_telemetry_updated(self, telemetry: VehicleTelemetry):
        self.telemetry = telemetry

    def on_render_tick(self):
        """Dispatches telemetry data to all visual widgets at 60 FPS."""
        self.header.update_telemetry(self.telemetry)
        self.battery_panel.update_telemetry(self.telemetry)
        self.center_dial.update_telemetry(self.telemetry)
        self.telemetry_panel.update_telemetry(self.telemetry)
        self.footer.update_telemetry(self.telemetry)

    def keyPressEvent(self, event: QKeyEvent):
        """Keyboard shortcuts."""
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_T:
            # Toggle between EVA Rei and Cyberpunk themes
            self.toggle_theme()
        elif event.key() == Qt.Key_M:
            # Toggle between Mock and Hardware
            self.force_mock = not self.force_mock
            print(f"[CivicDashboard] Toggling mode. Force Mock: {self.force_mock}")
            self.init_telemetry_source()
        elif event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.reader_thread:
            self.reader_thread.stop()
        event.accept()


def main():
    parser = argparse.ArgumentParser(description="Civic e:HEV (FL4) EVA & Cyberpunk OBD2 Dashboard")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port for OBD adapter (e.g. /dev/ttyUSB0 or /dev/rfcomm0)")
    parser.add_argument("--mock", action="store_true", help="Force Mock driving simulator mode")
    parser.add_argument("--theme", type=str, default="eva", choices=["eva", "cyberpunk"], help="UI theme: 'eva' (NERV Rei Ayanami) or 'cyberpunk'")
    parser.add_argument("--fullscreen", action="store_true", help="Launch in fullscreen kiosk mode")
    parser.add_argument("--width", type=int, default=1280, help="Initial window width (default: 1280)")
    parser.add_argument("--height", type=int, default=720, help="Initial window height (default: 720)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = CivicDashboardWindow(
        port=args.port,
        force_mock=args.mock,
        fullscreen=args.fullscreen,
        width=args.width,
        height=args.height,
        theme=args.theme
    )
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
