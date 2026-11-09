"""
Header & Footer Widgets: Tactical Title Bar, CAN Live Telemetry Matrix, and Status Footer
Supports:
- "eva": Neon Genesis Evangelion NERV MAGI Command HUD
- "cyberpunk": Cyberpunk Neon Glass Cockpit
"""

import time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QRectF, QPointF
from themes.cyberpunk_theme import CyberTheme
from themes.eva_theme import EvaTheme
from core.telemetry import VehicleTelemetry


class HeaderWidget(QWidget):
    def __init__(self, parent=None, theme="eva"):
        super().__init__(parent)
        self.telemetry = VehicleTelemetry()
        self.blink = True
        self.counter = 0
        self.rx_activity = 0
        self.theme = theme

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def update_telemetry(self, telemetry: VehicleTelemetry):
        self.telemetry = telemetry
        self.counter += 1
        if self.counter % 25 == 0:
            self.blink = not self.blink
        self.rx_activity = (self.rx_activity + 1) % 8
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        W, H = self.width(), self.height()
        is_eva = self.theme == "eva"

        if is_eva:
            # ==========================================
            # AUTHENTIC EVA CONCEPT HEADER
            # ==========================================
            # Base dark bar
            top_bar = QRectF(6, 4, W - 12, H - 8)
            painter.fillRect(top_bar, QColor(8, 6, 14, 250))
            painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(top_bar)

            # Left Tactical Callsign Pill (clean, high-tech, no red clutter)
            callsign_rect = QRectF(16, 7, 220, H - 14)
            painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.2))
            painter.setBrush(QBrush(QColor(12, 10, 20, 240)))
            painter.drawRoundedRect(callsign_rect, 3, 3)

            EvaTheme.draw_hazard_stripes(painter, QRectF(20, 10, 24, H - 20),
                                         stripe_color=EvaTheme.NERV_ORANGE, stripe_width=3, step=6, border=False)

            painter.setFont(EvaTheme.get_font(9, bold=True, mono=True))
            painter.setPen(EvaTheme.NERV_AMBER)
            painter.drawText(QRectF(50, 7, 180, H - 14), Qt.AlignVCenter | Qt.AlignLeft, "EVA-00 TACTICAL HUD")

            # Right System Status Tag
            status_w = 210
            status_rect = QRectF(W - 16 - status_w, 7, status_w, H - 14)
            painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.2))
            painter.setBrush(QBrush(QColor(12, 10, 20, 240)))
            painter.drawRoundedRect(status_rect, 3, 3)

            painter.setFont(EvaTheme.get_font(9, bold=True, mono=True))
            painter.setPen(EvaTheme.EVA_GREEN)
            painter.drawText(QRectF(W - 14 - status_w, 7, status_w - 38, H - 14), Qt.AlignVCenter | Qt.AlignRight, "MAGI SYNC : ACTIVE")

            EvaTheme.draw_hazard_stripes(painter, QRectF(W - 42, 10, 24, H - 20),
                                         stripe_color=EvaTheme.NERV_ORANGE, stripe_width=3, step=6, border=False)

            # Center Title: AUTHENTIC NERV COCKPIT / FL4 e:HEV HUD-HUD
            center_x = W / 2.0
            painter.setFont(EvaTheme.get_serif_font(13, bold=True))
            painter.setPen(EvaTheme.TEXT_WHITE)
            painter.drawText(QRectF(center_x - 170, 5, 340, 18), Qt.AlignCenter, "AUTHENTIC NERV COCKPIT")

            painter.setFont(EvaTheme.get_font(9, bold=True, mono=True))
            painter.setPen(QColor(176, 102, 255))
            painter.drawText(QRectF(center_x - 170, 23, 340, 15), Qt.AlignCenter, "FL4 e:HEV HUD-HUD")

            # Blinking Heartbeat Beacon & Activity Indicator
            beacon_x = int(center_x + 135)
            beacon_y = int(H / 2)
            dot_color = EvaTheme.EVA_GREEN if self.telemetry.is_connected else EvaTheme.NERV_AMBER
            if self.blink:
                painter.setPen(QPen(QColor(dot_color.red(), dot_color.green(), dot_color.blue(), 120), 1.5))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QPointF(beacon_x, beacon_y), 7, 7)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(dot_color))
            painter.drawEllipse(QPointF(beacon_x, beacon_y), 3.5, 3.5)

            # Left side activity dots
            dot_start_x = int(center_x - 150)
            for d in range(3):
                is_active = (self.rx_activity + d) % 3 == 0
                d_color = EvaTheme.EVA_GREEN if is_active else EvaTheme.GRID_LINE_BRIGHT
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(d_color))
                painter.drawEllipse(QPointF(dot_start_x - d * 8, beacon_y), 2.5, 2.5)

            return

        # Cyberpunk Theme Top Tech Bevel Frame with chamfered wings
        top_bar = QRectF(6, 4, W - 12, H - 8)
        c = 10.0
        x, y, w, h = top_bar.x(), top_bar.y(), top_bar.width(), top_bar.height()

        path = QPainterPath()
        path.moveTo(x + c, y)
        path.lineTo(x + w - c, y)
        path.lineTo(x + w, y + c)
        path.lineTo(x + w - c * 2, y + h)
        path.lineTo(x + c * 2, y + h)
        path.lineTo(x, y + c)
        path.closeSubpath()

        painter.setPen(QPen(CyberTheme.CYAN_DIM, 1.2))
        painter.setBrush(QBrush(CyberTheme.BG_CARD))
        painter.drawPath(path)

        painter.setPen(QPen(CyberTheme.CYAN_DIM, 1.5))
        for i in range(3):
            lx = x + c * 2 + 8 + i * 6
            painter.drawLine(int(lx), int(y + h - 6), int(lx + 4), int(y + 6))

        # Left Tag: Vehicle Tactical Callsign Pill
        callsign_w = 140
        callsign_rect = QRectF(x + c * 2 + 36, y + 5, callsign_w, h - 10)
        painter.setPen(QPen(CyberTheme.CYAN_CORE, 1.2))
        painter.setBrush(QBrush(QColor(0, 240, 255, 18)))
        painter.drawRoundedRect(callsign_rect, 3, 3)

        painter.setFont(CyberTheme.get_font(10, bold=True, mono=True))
        painter.setPen(CyberTheme.CYAN_BRIGHT)
        painter.drawText(callsign_rect, Qt.AlignCenter, "CIVIC e:HEV FL4")

        # CAN RX Activity Indicator Dots
        dot_start_x = int(callsign_rect.right() + 12)
        dot_y = int(y + h / 2)
        for d in range(3):
            is_active = (self.rx_activity + d) % 3 == 0
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(CyberTheme.NEON_GREEN if is_active else CyberTheme.GRID_LINE_BRIGHT))
            painter.drawEllipse(QPointF(dot_start_x + d * 8, dot_y), 2.5, 2.5)

        # Center Title
        painter.setFont(CyberTheme.get_font(12, bold=True, mono=True))
        painter.setPen(CyberTheme.TEXT_WHITE)
        painter.drawText(QRectF(0, y - 2, W, h), Qt.AlignCenter, "CAN 500kbps LIVE")

        # Heartbeat Beacon
        beacon_x = int(W / 2 + 116)
        beacon_y = int(y + h / 2)
        dot_color = CyberTheme.NEON_GREEN if self.telemetry.is_connected else CyberTheme.AMBER_CORE
        if self.blink:
            painter.setPen(QPen(QColor(dot_color.red(), dot_color.green(), dot_color.blue(), 120), 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(beacon_x, beacon_y), 7, 7)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(dot_color))
        painter.drawEllipse(QPointF(beacon_x, beacon_y), 4, 4)

        # Right Tag
        painter.setFont(CyberTheme.get_font(9, bold=True, mono=True))
        painter.setPen(CyberTheme.TEXT_MUTED)
        painter.drawText(int(W - 225), int(H / 2 + 4), "SYS: NOMINAL // ECU: 7E0/7E2")


class FooterWidget(QWidget):
    def __init__(self, parent=None, theme="eva"):
        super().__init__(parent)
        self.telemetry = VehicleTelemetry()
        self.theme = theme

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def update_telemetry(self, telemetry: VehicleTelemetry):
        self.telemetry = telemetry
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        W, H = self.width(), self.height()
        is_eva = self.theme == "eva"

        if is_eva:
            # ==========================================
            # AUTHENTIC EVA CONCEPT FOOTER
            # ==========================================
            # Base dark bar
            bot_bar = QRectF(6, 4, W - 12, H - 8)
            painter.fillRect(bot_bar, QColor(8, 6, 14, 250))
            painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(bot_bar)

            # Center Red Trapezoid Tab: WARNING NERV
            trap_cx = W / 2.0
            trap_top_w = 175.0
            trap_bot_w = 210.0
            poly_trap = QPolygonF([
                QPointF(trap_cx - trap_top_w / 2.0, 4),
                QPointF(trap_cx + trap_top_w / 2.0, 4),
                QPointF(trap_cx + trap_bot_w / 2.0, H - 4),
                QPointF(trap_cx - trap_bot_w / 2.0, H - 4)
            ])
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(EvaTheme.EVA_RED_BANNER))
            painter.drawPolygon(poly_trap)

            painter.setFont(EvaTheme.get_serif_font(11, bold=True))
            painter.setPen(EvaTheme.TEXT_WHITE)
            painter.drawText(QRectF(trap_cx - 100, 4, 200, H - 8), Qt.AlignCenter, "WARNING NERV")

            # Left Clock with NERV Green Display
            time_str = time.strftime("%H:%M:%S")
            painter.setFont(EvaTheme.get_serif_font(12, bold=True))
            painter.setPen(EvaTheme.EVA_GREEN)
            painter.drawText(24, int(H / 2 + 5), f"⏱ {time_str} JST")

            # Far-Right PRND Gear Selector Strip
            gears = ["P", "R", "N", "D", "B"]
            curr_gear = self.telemetry.gear.upper()
            box_w = 26
            box_h = 20
            box_gap = 5
            total_gear_w = len(gears) * box_w + (len(gears) - 1) * box_gap
            gear_start_x = int(W - 24 - total_gear_w)
            box_y = int(H / 2 - box_h / 2)

            for idx, g in enumerate(gears):
                gx = gear_start_x + idx * (box_w + box_gap)
                is_active = (g == curr_gear)
                g_rect = QRectF(gx, box_y, box_w, box_h)

                if is_active:
                    painter.setPen(QPen(EvaTheme.NERV_ORANGE, 1.6))
                    painter.setBrush(QBrush(QColor(255, 102, 0, 70)))
                    painter.drawRect(g_rect)
                    painter.setFont(EvaTheme.get_font(11, bold=True, mono=True))
                    painter.setPen(EvaTheme.NERV_ORANGE)
                    painter.drawText(g_rect, Qt.AlignCenter, g)
                else:
                    painter.setPen(QPen(QColor(40, 30, 50), 1.0))
                    painter.setBrush(QBrush(QColor(12, 10, 18, 180)))
                    painter.drawRect(g_rect)
                    painter.setFont(EvaTheme.get_font(10, bold=False, mono=True))
                    painter.setPen(EvaTheme.TEXT_DIM)
                    painter.drawText(g_rect, Qt.AlignCenter, g)

            return

        # Cyberpunk Theme Bottom Frame
        bot_bar = QRectF(6, 4, W - 12, H - 8)
        painter.setPen(QPen(CyberTheme.GRID_LINE_BRIGHT, 1))
        painter.setBrush(QBrush(CyberTheme.BG_CARD))
        painter.drawRoundedRect(bot_bar, 4, 4)

        time_str = time.strftime("%H:%M:%S")
        painter.setFont(CyberTheme.get_font(10, bold=True, mono=True))
        painter.setPen(CyberTheme.CYAN_BRIGHT)
        painter.drawText(22, int(H / 2 + 4), f"⏱ {time_str}")

        # Center Telemetry
        painter.setFont(CyberTheme.get_font(10, bold=True, mono=True))
        painter.setPen(CyberTheme.CYAN_CORE)
        g_str = f"◀ LAT: {self.telemetry.g_lat:+.2f}G   LONG: {self.telemetry.g_long:+.2f}G   PEAK: {self.telemetry.g_peak:.2f}G ▶"
        painter.drawText(QRectF(0, 0, W, H), Qt.AlignCenter, g_str)

        # Right PRND Gear Selector Strip
        gears = ["P", "R", "N", "D", "B"]
        curr_gear = self.telemetry.gear.upper()
        gear_start_x = int(W - 170)
        box_y = int(H / 2 - 9)
        box_h = 18

        for idx, g in enumerate(gears):
            gx = gear_start_x + idx * 24
            is_active = (g == curr_gear)
            g_rect = QRectF(gx, box_y, 20, box_h)

            if is_active:
                gear_c = CyberTheme.AMBER_CORE
                painter.setPen(QPen(gear_c, 1.2))
                painter.setBrush(QBrush(QColor(gear_c.red(), gear_c.green(), gear_c.blue(), 45)))
                painter.drawRoundedRect(g_rect, 3, 3)
                painter.setFont(CyberTheme.get_font(10, bold=True, mono=True))
                painter.setPen(gear_c)
                painter.drawText(g_rect, Qt.AlignCenter, g)
            else:
                painter.setFont(CyberTheme.get_font(9, bold=False, mono=True))
                painter.setPen(CyberTheme.TEXT_DIM)
                painter.drawText(g_rect, Qt.AlignCenter, g)

        mode_str = "[ SIM ]" if self.telemetry.is_simulated else "[ OBD ]"
        painter.setFont(CyberTheme.get_font(9, bold=True, mono=True))
        painter.setPen(CyberTheme.TEXT_MUTED)
        painter.drawText(int(W - 235), int(H / 2 + 4), mode_str)

