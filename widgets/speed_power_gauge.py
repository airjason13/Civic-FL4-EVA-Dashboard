"""
Center Widget: Speedometer, Dual-Arc Power/Charge Gauge, & Tactical G-Force / A.T. FIELD Radar
Supports:
- "eva": Neon Genesis Evangelion Octagonal A.T. FIELD & NERV Target Lock-on
- "cyberpunk": Cyberpunk friction circle & tactical radar sweep
"""

import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QRadialGradient, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF
from themes.cyberpunk_theme import CyberTheme
from themes.eva_theme import EvaTheme
from core.telemetry import VehicleTelemetry


class SpeedPowerGaugeWidget(QWidget):
    def __init__(self, parent=None, theme="eva"):
        super().__init__(parent)
        self.telemetry = VehicleTelemetry()
        self.radar_angle = 0.0
        self.ripple_phase = 0.0
        self.g_trail = []
        self.theme = theme

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def update_telemetry(self, telemetry: VehicleTelemetry):
        self.telemetry = telemetry
        self.radar_angle = (self.radar_angle + 3.0) % 360.0
        self.ripple_phase = (self.ripple_phase + 0.08) % 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        W, H = self.width(), self.height()

        if self.theme == "eva":
            self.draw_eva_concept_gauge(painter, W, H)
            return

        center = QPointF(W / 2.0, H / 2.0)
        radius = min(W, H) * 0.46
        is_eva = False

        # 0. Flanking Tactical HUD Wings
        if (center.x() - radius) >= 8:
            wing_y_top = center.y() - radius * 0.72
            wing_y_bot = center.y() + radius * 0.72
            wing_lx = center.x() - radius - 14
            wing_rx = center.x() + radius + 4
            wing_h = wing_y_bot - wing_y_top
            wing_w = 10

            if is_eva:
                # Iconic NERV launch catapult hazard pillars flanking speed dial
                rect_l = QRectF(wing_lx, wing_y_top, wing_w, wing_h)
                rect_r = QRectF(wing_rx, wing_y_top, wing_w, wing_h)
                EvaTheme.draw_hazard_stripes(painter, rect_l, stripe_color=EvaTheme.NERV_ORANGE, stripe_width=4, step=8, border=True)
                EvaTheme.draw_hazard_stripes(painter, rect_r, stripe_color=EvaTheme.NERV_ORANGE, stripe_width=4, step=8, border=True)
            else:
                wing_color = CyberTheme.GRID_LINE_BRIGHT
                pen_wing = QPen(wing_color, 1.2)
                painter.setPen(pen_wing)

                # Left Wing
                painter.drawLine(int(wing_lx + 4), int(wing_y_top), int(wing_lx - 2), int(wing_y_top + 12))
                painter.drawLine(int(wing_lx - 2), int(wing_y_top + 12), int(wing_lx - 2), int(wing_y_bot - 12))
                painter.drawLine(int(wing_lx - 2), int(wing_y_bot - 12), int(wing_lx + 4), int(wing_y_bot))
                for w_tick in (-24, 0, 24):
                    ty = int(center.y() + w_tick)
                    painter.drawLine(int(wing_lx - 2), ty, int(wing_lx + 3), ty)

                # Right Wing
                painter.drawLine(int(wing_rx), int(wing_y_top), int(wing_rx + 6), int(wing_y_top + 12))
                painter.drawLine(int(wing_rx + 6), int(wing_y_top + 12), int(wing_rx + 6), int(wing_y_bot - 12))
                painter.drawLine(int(wing_rx + 6), int(wing_y_bot - 12), int(wing_rx), int(wing_y_bot))
                for w_tick in (-24, 0, 24):
                    ty = int(center.y() + w_tick)
                    painter.drawLine(int(wing_rx + 6), ty, int(wing_rx + 1), ty)

        # 1. Outer Tachometer Tick Ring (48 radial tick marks)
        dial_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        painter.save()
        painter.translate(center)

        spd_norm = min(1.0, max(0.0, self.telemetry.speed_kmh / 180.0))
        active_tick_count = int(round(spd_norm * 48))

        for i in range(48):
            angle = i * (360.0 / 48)
            is_major = (i % 6 == 0)
            is_lit = (i <= active_tick_count) and (self.telemetry.speed_kmh > 3)

            if is_eva:
                if is_lit:
                    pen_color = EvaTheme.NERV_ORANGE if is_major else EvaTheme.NERV_AMBER
                    tick_pen = QPen(pen_color, 2.2 if is_major else 1.5)
                else:
                    pen_color = EvaTheme.EVA_PURPLE if is_major else EvaTheme.GRID_LINE_BRIGHT
                    tick_pen = QPen(pen_color, 1.8 if is_major else 1.0)
            else:
                if is_lit:
                    pen_color = CyberTheme.CYAN_CORE if is_major else CyberTheme.CYAN_DIM
                    tick_pen = QPen(pen_color, 2.2 if is_major else 1.5)
                else:
                    pen_color = CyberTheme.CYAN_DIM if is_major else CyberTheme.GRID_LINE_BRIGHT
                    tick_pen = QPen(pen_color, 1.8 if is_major else 1.0)

            painter.setPen(tick_pen)
            tick_len = 10 if is_major else 5
            rad = math.radians(angle)
            p1 = QPointF((radius + 2) * math.cos(rad), (radius + 2) * math.sin(rad))
            p2 = QPointF((radius + 2 + tick_len) * math.cos(rad), (radius + 2 + tick_len) * math.sin(rad))
            painter.drawLine(p1, p2)
        painter.restore()

        # Base Gauge Ring
        ring_bg = EvaTheme.BG_CARD if is_eva else CyberTheme.BG_CARD
        ring_border = EvaTheme.EVA_PURPLE if is_eva else CyberTheme.GRID_LINE
        painter.setPen(QPen(ring_border, 8, Qt.SolidLine))
        painter.setBrush(QBrush(ring_bg))
        painter.drawEllipse(center, radius, radius)

        # 2. Dual-Arc Dynamic Power / Charge Meter
        power_kw = self.telemetry.motor_power_kw

        # Static Track Guides
        guide_c1 = EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_DIM
        guide_c2 = EvaTheme.NERV_AMBER if is_eva else CyberTheme.AMBER_DIM
        painter.setPen(QPen(guide_c1, 3))
        painter.drawArc(dial_rect, 135 * 16, 90 * 16)  # Charge guide
        painter.setPen(QPen(guide_c2, 3))
        painter.drawArc(dial_rect, -45 * 16, 90 * 16)  # Power guide

        # Dynamic Power/Charge Arc
        if power_kw < 0:
            # Regenerative Braking
            pct = min(1.0, abs(power_kw) / 50.0)
            span = int(90.0 * pct * 16)
            arc_c = EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_CORE
            painter.setPen(QPen(QColor(arc_c.red(), arc_c.green(), arc_c.blue(), 60), 14, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(dial_rect, 180 * 16, span)
            painter.setPen(QPen(arc_c, 8, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(dial_rect, 180 * 16, span)

            # Tip
            tip_deg = 180.0 + (90.0 * pct)
            tip_rad = math.radians(-tip_deg)
            tx = center.x() + radius * math.cos(tip_rad)
            ty = center.y() + radius * math.sin(tip_rad)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(EvaTheme.TEXT_WHITE))
            painter.drawEllipse(QPointF(tx, ty), 4, 4)
            painter.setBrush(Qt.NoBrush)
        else:
            # Power Output
            pct = min(1.0, power_kw / 120.0)
            span = int(-90.0 * pct * 16)
            arc_c = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.AMBER_CORE
            painter.setPen(QPen(QColor(arc_c.red(), arc_c.green(), arc_c.blue(), 60), 14, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(dial_rect, 0 * 16, span)
            painter.setPen(QPen(arc_c, 8, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(dial_rect, 0 * 16, span)

            tip_deg = 0.0 - (90.0 * pct)
            tip_rad = math.radians(-tip_deg)
            tx = center.x() + radius * math.cos(tip_rad)
            ty = center.y() + radius * math.sin(tip_rad)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(EvaTheme.TEXT_WHITE))
            painter.drawEllipse(QPointF(tx, ty), 4, 4)
            painter.setBrush(Qt.NoBrush)

        # 3. Inner Dial Face & Labels
        inner_radius = radius - 26
        painter.setPen(QPen(EvaTheme.GRID_LINE_BRIGHT if is_eva else CyberTheme.GRID_LINE_BRIGHT, 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, inner_radius, inner_radius)

        label_font = EvaTheme.get_font(9, bold=True, mono=True) if is_eva else CyberTheme.get_font(9, bold=True, mono=True)
        painter.setFont(label_font)
        painter.setPen(EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_CORE)
        painter.drawText(int(center.x() - radius * 0.72), int(center.y() - radius * 0.48), "CHG" if not is_eva else "REGEN")

        painter.setPen(EvaTheme.NERV_ORANGE if is_eva else CyberTheme.AMBER_CORE)
        painter.drawText(int(center.x() + radius * 0.52), int(center.y() - radius * 0.48), "PWR" if not is_eva else "OUTPUT")

        # 4. UPPER HALF: Massive Digital Speed Display
        speed_val = int(round(self.telemetry.speed_kmh))
        speed_str = f"{speed_val}"
        speed_font = EvaTheme.get_font(56, bold=True) if is_eva else CyberTheme.get_font(52, bold=True)
        painter.setFont(speed_font)
        painter.setPen(EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE)

        speed_rect = QRectF(center.x() - 110, center.y() - radius * 0.65, 220, 68)
        painter.drawText(speed_rect, Qt.AlignCenter, speed_str)

        unit_font = EvaTheme.get_font(10, bold=True, mono=True) if is_eva else CyberTheme.get_font(10, bold=True)
        painter.setFont(unit_font)
        painter.setPen(EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_CORE)
        painter.drawText(int(center.x() + 52), int(center.y() - radius * 0.32), "km/h")

        # EV / HYBRID Mode Tactical Pill
        is_ev = self.telemetry.drive_mode == "EV"
        pill_w, pill_h = 108 if is_eva else 96, 22
        pill_rect = QRectF(center.x() - pill_w / 2, center.y() - radius * 0.14, pill_w, pill_h)
        pill_color = EvaTheme.ACID_GREEN if is_ev else EvaTheme.NERV_ORANGE if is_eva else (CyberTheme.CYAN_CORE if is_ev else CyberTheme.AMBER_CORE)

        if is_eva:
            mode_text = "⚡ INTERNAL" if is_ev else "⚙ UMBILICAL"
            EvaTheme.draw_hazard_badge(painter, pill_rect, mode_text, stripe_color=pill_color, text_color=pill_color, font_size=8)
        else:
            painter.setPen(QPen(pill_color, 1.2))
            painter.setBrush(QBrush(QColor(pill_color.red(), pill_color.green(), pill_color.blue(), 25)))
            painter.drawRoundedRect(pill_rect, 4, 4)

            painter.setFont(CyberTheme.get_font(10, bold=True))
            painter.setPen(pill_color)
            mode_text = "⚡ EV MODE" if is_ev else "⚙ HYBRID"
            painter.drawText(pill_rect, Qt.AlignCenter, mode_text)

        # Horizontal Center Grid Line
        painter.setPen(QPen(EvaTheme.GRID_LINE_BRIGHT if is_eva else CyberTheme.GRID_LINE_BRIGHT, 1.5))
        cy = int(center.y() + 6)
        painter.drawLine(int(center.x() - inner_radius * 0.75), cy, int(center.x() - 30), cy)
        painter.drawLine(int(center.x() + 30), cy, int(center.x() + inner_radius * 0.75), cy)

        # Center diamond accent
        diamond = QPainterPath()
        diamond.moveTo(center.x(), cy - 5)
        diamond.lineTo(center.x() + 6, cy)
        diamond.lineTo(center.x(), cy + 5)
        diamond.lineTo(center.x() - 6, cy)
        diamond.closeSubpath()
        painter.setPen(QPen(pill_color, 1))
        painter.setBrush(QBrush(pill_color))
        painter.drawPath(diamond)
        painter.setBrush(Qt.NoBrush)

        # 5. LOWER HALF: G-Force Radar & A.T. FIELD
        g_center = QPointF(center.x(), center.y() + radius * 0.36)
        g_max_r = radius * 0.28
        curr_g = math.sqrt(self.telemetry.g_lat**2 + self.telemetry.g_long**2)
        high_g = curr_g > 0.45

        # 5.1 Radar Background
        grad_radar = QRadialGradient(g_center.x(), g_center.y(), g_max_r)
        grad_radar.setColorAt(0.0, QColor(8, 8, 14, 220))
        grad_radar.setColorAt(0.65, QColor(6, 6, 12, 235))
        grad_radar.setColorAt(1.0, QColor(14, 10, 22, 255))
        painter.setBrush(QBrush(grad_radar))
        border_radar = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_DIM
        painter.setPen(QPen(border_radar, 1.2, Qt.SolidLine))
        painter.drawEllipse(g_center, g_max_r, g_max_r)
        painter.setBrush(Qt.NoBrush)

        # 5.2 Concentric Barriers: Octagonal A.T. Field in EVA Mode!
        if is_eva:
            # Concentric Octagonal A.T. FIELD barriers
            field_pulse = self.radar_angle * 0.05
            EvaTheme.draw_at_field(painter, g_center, g_max_r, layers=4, pulse_offset=field_pulse)
        else:
            painter.setPen(QPen(CyberTheme.GRID_LINE_BRIGHT, 1, Qt.DotLine))
            painter.drawEllipse(g_center, g_max_r * 0.33, g_max_r * 0.33)  # 0.5G
            painter.drawEllipse(g_center, g_max_r * 0.66, g_max_r * 0.66)  # 1.0G
            painter.setPen(QPen(CyberTheme.CYAN_DIM, 1.2, Qt.SolidLine))
            painter.drawEllipse(g_center, g_max_r, g_max_r)

        # 5.3 Reticle Outer Brackets
        brk = 8
        b_r = g_max_r + 4
        bracket_c = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_DIM
        painter.setPen(QPen(bracket_c, 1.5))
        painter.drawLine(int(g_center.x() - b_r), int(g_center.y() - b_r + brk), int(g_center.x() - b_r), int(g_center.y() - b_r))
        painter.drawLine(int(g_center.x() - b_r), int(g_center.y() - b_r), int(g_center.x() - b_r + brk), int(g_center.y() - b_r))
        painter.drawLine(int(g_center.x() + b_r - brk), int(g_center.y() - b_r), int(g_center.x() + b_r), int(g_center.y() - b_r))
        painter.drawLine(int(g_center.x() + b_r), int(g_center.y() - b_r), int(g_center.x() + b_r), int(g_center.y() - b_r + brk))
        painter.drawLine(int(g_center.x() - b_r), int(g_center.y() + b_r - brk), int(g_center.x() - b_r), int(g_center.y() + b_r))
        painter.drawLine(int(g_center.x() - b_r), int(g_center.y() + b_r), int(g_center.x() - b_r + brk), int(g_center.y() + b_r))
        painter.drawLine(int(g_center.x() + b_r - brk), int(g_center.y() + b_r), int(g_center.x() + b_r), int(g_center.y() + b_r))
        painter.drawLine(int(g_center.x() + b_r), int(g_center.y() + b_r), int(g_center.x() + b_r), int(g_center.y() + b_r - brk))

        # 5.4 Crosshairs
        cross_c = EvaTheme.NERV_RED if (is_eva and high_g) else (EvaTheme.GRID_LINE_BRIGHT if is_eva else CyberTheme.GRID_LINE_BRIGHT)
        painter.setPen(QPen(cross_c, 1))
        painter.drawLine(int(g_center.x() - g_max_r - 6), int(g_center.y()),
                         int(g_center.x() + g_max_r + 6), int(g_center.y()))
        painter.drawLine(int(g_center.x()), int(g_center.y() - g_max_r - 6),
                         int(g_center.x()), int(g_center.y() + g_max_r + 6))

        # 5.5 Sweeping Radar Cone
        sweep_path = QPainterPath()
        sweep_path.moveTo(g_center)
        sweep_path.arcTo(QRectF(g_center.x() - g_max_r, g_center.y() - g_max_r, g_max_r * 2, g_max_r * 2), -self.radar_angle, -35)
        sweep_path.closeSubpath()
        painter.setPen(Qt.NoPen)
        sweep_fill = QColor(255, 102, 0, 25) if is_eva else QColor(0, 240, 255, 26)
        painter.setBrush(QBrush(sweep_fill))
        painter.drawPath(sweep_path)
        painter.setBrush(Qt.NoBrush)

        radar_rad = math.radians(self.radar_angle)
        rx = g_center.x() + g_max_r * math.cos(radar_rad)
        ry = g_center.y() + g_max_r * math.sin(radar_rad)
        beam_c = QColor(255, 102, 0, 80) if is_eva else QColor(0, 240, 255, 80)
        painter.setPen(QPen(beam_c, 1.5))
        painter.drawLine(g_center, QPointF(rx, ry))

        # 5.6 Directional Cardinal Markers
        painter.setFont(EvaTheme.get_font(7, bold=True, mono=True) if is_eva else CyberTheme.get_font(7, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED)
        painter.drawText(int(g_center.x() - 10), int(g_center.y() - g_max_r + 10), "FWD")
        painter.drawText(int(g_center.x() - 10), int(g_center.y() + g_max_r - 4), "BRK")
        painter.drawText(int(g_center.x() - g_max_r + 3), int(g_center.y() + 3), "L")
        painter.drawText(int(g_center.x() + g_max_r - 9), int(g_center.y() + 3), "R")

        # 5.7 G-Force Dot Position Calculation
        dot_x = g_center.x() + (self.telemetry.g_lat / 1.5) * g_max_r
        dot_y = g_center.y() - (self.telemetry.g_long / 1.5) * g_max_r

        dist = math.hypot(dot_x - g_center.x(), dot_y - g_center.y())
        if dist > g_max_r:
            angle = math.atan2(dot_y - g_center.y(), dot_x - g_center.x())
            dot_x = g_center.x() + g_max_r * math.cos(angle)
            dot_y = g_center.y() + g_max_r * math.sin(angle)

        self.g_trail.append((dot_x, dot_y))
        if len(self.g_trail) > 8:
            self.g_trail.pop(0)

        for idx in range(1, len(self.g_trail)):
            p_prev = QPointF(self.g_trail[idx - 1][0], self.g_trail[idx - 1][1])
            p_curr = QPointF(self.g_trail[idx][0], self.g_trail[idx][1])
            trail_alpha = int(25 + (idx / len(self.g_trail)) * 110)
            trail_color = QColor(255, 102, 0, trail_alpha) if is_eva else QColor(0, 240, 255, trail_alpha)
            painter.setPen(QPen(trail_color, 1.8))
            painter.drawLine(p_prev, p_curr)

        # Dynamic G-Vector Line
        painter.setPen(QPen(bracket_c, 1.5, Qt.DashLine))
        painter.drawLine(g_center, QPointF(dot_x, dot_y))

        # Expanding Ripple around G-dot
        ripple_r = 6.0 + (self.ripple_phase * 16.0)
        ripple_alpha = int(220 * (1.0 - self.ripple_phase))
        rip_c = QColor(255, 26, 42, ripple_alpha) if (is_eva and high_g) else (QColor(255, 102, 0, ripple_alpha) if is_eva else QColor(0, 240, 255, ripple_alpha))
        painter.setPen(QPen(rip_c, 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(dot_x, dot_y), ripple_r, ripple_r)

        # Tracking Dot
        painter.setPen(Qt.NoPen)
        grad_dot = QRadialGradient(dot_x, dot_y, 9)
        dot_c1 = EvaTheme.NERV_RED if is_eva else CyberTheme.CYAN_BRIGHT
        dot_c2 = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_CORE
        grad_dot.setColorAt(0.0, dot_c1)
        grad_dot.setColorAt(0.4, dot_c2)
        grad_dot.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad_dot))
        painter.drawEllipse(QPointF(dot_x, dot_y), 8, 8)

        painter.setBrush(QBrush(EvaTheme.TEXT_WHITE))
        painter.drawEllipse(QPointF(dot_x, dot_y), 3, 3)
        painter.setBrush(Qt.NoBrush)

        # 5.8 Digital Readout with A.T. Field Indicator
        painter.setFont(EvaTheme.get_font(12, bold=True, mono=True) if is_eva else CyberTheme.get_font(12, bold=True, mono=True))
        g_pen_c = (EvaTheme.NERV_RED if high_g else EvaTheme.NERV_ORANGE) if is_eva else CyberTheme.CYAN_CORE
        painter.setPen(g_pen_c)
        if is_eva:
            g_text = f"[ ! A.T. FIELD ! {curr_g:.2f}G ]" if high_g else f"[ A.T. FIELD: {curr_g:.2f}G ]"
        else:
            g_text = f"[ {curr_g:.2f} G ]"
        g_rect = QRectF(center.x() - 110, center.y() + radius * 0.68, 220, 20)
        painter.drawText(g_rect, Qt.AlignCenter, g_text)

        # Fine Dual-Axis Readout
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True) if is_eva else CyberTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED)
        sub_text = f"LAT:{self.telemetry.g_lat:+.2f}G  LON:{self.telemetry.g_long:+.2f}G"
        sub_rect = QRectF(center.x() - 110, center.y() + radius * 0.81, 220, 16)
        painter.drawText(sub_rect, Qt.AlignCenter, sub_text)

    def draw_eva_concept_gauge(self, painter, W, H):
        """
        Renders the authentic Evangelion concept center gauge:
        - Flanking neon acid-green and warm orange angled brackets: ( [  ] )
        - Concentric circular targeting reticle with crosshairs
        - Top radial chevron tick arc at 12 o'clock (NERV lock-on sight)
        - Moving G-force target tracking box
        - Giant pale-cream serif speed numerals in #fff8b0 with km/h
        - G-FORCE LOCK-ON subtitle in #00ff40
        - Tactical internal/umbilical power mode badge
        """
        cx, cy = W / 2.0, H / 2.0
        radius = min(W, H) * 0.44

        # 0. Outer Card Background
        card_rect = QRectF(6, 6, W - 12, H - 12)
        painter.fillRect(card_rect, QColor(6, 4, 10, 245))

        # Subtle NERV purple frame
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(card_rect)

        # Flanking vertical hazard pillars on far left/right of center gauge
        pillar_w = 10
        pillar_h = H * 0.65
        pillar_y = (H - pillar_h) / 2.0
        EvaTheme.draw_hazard_stripes(painter, QRectF(14, pillar_y, pillar_w, pillar_h),
                                     stripe_color=EvaTheme.NERV_ORANGE, stripe_width=3, step=7, border=True)
        EvaTheme.draw_hazard_stripes(painter, QRectF(W - 24, pillar_y, pillar_w, pillar_h),
                                     stripe_color=EvaTheme.NERV_ORANGE, stripe_width=3, step=7, border=True)

        # 1. Concentric Target Reticle Circles
        r_outer = radius * 0.88
        r_mid = radius * 0.62
        r_inner = radius * 0.38

        # Outer dotted circle
        painter.setPen(QPen(QColor(84, 32, 132, 180), 1.2, Qt.DashLine))
        painter.drawEllipse(QPointF(cx, cy), r_outer, r_outer)

        # Mid amber circle
        painter.setPen(QPen(QColor(208, 120, 16, 120), 1.2, Qt.SolidLine))
        painter.drawEllipse(QPointF(cx, cy), r_mid, r_mid)

        # Inner fine circle
        painter.setPen(QPen(QColor(255, 102, 0, 90), 1.0, Qt.DotLine))
        painter.drawEllipse(QPointF(cx, cy), r_inner, r_inner)

        # 2. Cardinal Crosshairs with graduation ticks
        painter.setPen(QPen(QColor(208, 120, 16, 160), 1.0))
        # Horizontal crosshair line
        painter.drawLine(int(cx - r_outer - 15), int(cy), int(cx + r_outer + 15), int(cy))
        # Vertical crosshair line
        painter.drawLine(int(cx), int(cy - r_outer - 15), int(cx), int(cy + r_outer + 15))

        # Crosshair graduation tick marks
        for tick_d in (-r_mid, -r_inner, r_inner, r_mid):
            painter.drawLine(int(cx + tick_d), int(cy - 4), int(cx + tick_d), int(cy + 4))
            painter.drawLine(int(cx - 4), int(cy + tick_d), int(cx + 4), int(cy + tick_d))

        # 3. Top Radial Chevron Arc / Lock-on Sight (12 o'clock / -90 deg)
        # Red chevron arc spanning -115 deg to -65 deg
        top_arc_rect = QRectF(cx - r_outer - 8, cy - r_outer - 8, (r_outer + 8) * 2, (r_outer + 8) * 2)
        painter.setPen(QPen(EvaTheme.NERV_RED, 2.5, Qt.SolidLine))
        painter.drawArc(top_arc_rect, int(65 * 16), int(50 * 16))

        # Radiating red tick marks at 12 o'clock
        for deg in (-115, -105, -95, -85, -75, -65):
            rad = math.radians(deg)
            p_start = QPointF(cx + (r_outer + 4) * math.cos(rad), cy + (r_outer + 4) * math.sin(rad))
            p_end = QPointF(cx + (r_outer + 14) * math.cos(rad), cy + (r_outer + 14) * math.sin(rad))
            painter.drawLine(p_start, p_end)

        # Downward lock-on triangle at top apex
        apex_y = cy - r_outer - 12
        poly_apex = QPolygonF([
            QPointF(cx - 6, apex_y - 6),
            QPointF(cx + 6, apex_y - 6),
            QPointF(cx, apex_y + 1)
        ])
        painter.setBrush(QBrush(EvaTheme.NERV_RED))
        painter.drawPolygon(poly_apex)
        painter.setBrush(Qt.NoBrush)

        # 4. Flanking Neon Acid-Green & Warm Orange Brackets: ( [   ] )
        # Outer Green Chamfered Brackets
        painter.setPen(QPen(EvaTheme.EVA_GREEN, 3.5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        b_gw = radius * 0.78
        b_gh = radius * 0.58
        chamfer = 24.0

        # Left Green Bracket '('
        path_gl = QPainterPath()
        path_gl.moveTo(cx - b_gw + chamfer, cy - b_gh)
        path_gl.lineTo(cx - b_gw, cy - b_gh + chamfer)
        path_gl.lineTo(cx - b_gw, cy + b_gh - chamfer)
        path_gl.lineTo(cx - b_gw + chamfer, cy + b_gh)
        painter.drawPath(path_gl)

        # Right Green Bracket ')'
        path_gr = QPainterPath()
        path_gr.moveTo(cx + b_gw - chamfer, cy - b_gh)
        path_gr.lineTo(cx + b_gw, cy - b_gh + chamfer)
        path_gr.lineTo(cx + b_gw, cy + b_gh - chamfer)
        path_gr.lineTo(cx + b_gw - chamfer, cy + b_gh)
        painter.drawPath(path_gr)

        # Inner Orange Brackets '[' and ']'
        painter.setPen(QPen(EvaTheme.NERV_ORANGE, 2.5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        b_ow = radius * 0.60
        b_oh = radius * 0.46
        inner_fin = 16.0

        # Left Orange Bracket '['
        path_ol = QPainterPath()
        path_ol.moveTo(cx - b_ow + inner_fin, cy - b_oh)
        path_ol.lineTo(cx - b_ow, cy - b_oh)
        path_ol.lineTo(cx - b_ow, cy + b_oh)
        path_ol.lineTo(cx - b_ow + inner_fin, cy + b_oh)
        painter.drawPath(path_ol)

        # Right Orange Bracket ']'
        path_or = QPainterPath()
        path_or.moveTo(cx + b_ow - inner_fin, cy - b_oh)
        path_or.lineTo(cx + b_ow, cy - b_oh)
        path_or.lineTo(cx + b_ow, cy + b_oh)
        path_or.lineTo(cx + b_ow - inner_fin, cy + b_oh)
        painter.drawPath(path_or)

        # 5. Dynamic G-Force Target Reticle & Tracking Point
        curr_g = math.sqrt(self.telemetry.g_lat**2 + self.telemetry.g_long**2)
        dot_x = cx + (self.telemetry.g_lat / 1.5) * (r_inner * 0.9)
        dot_y = cy - (self.telemetry.g_long / 1.5) * (r_inner * 0.9)

        # Target Tracking Square around dot [ + ]
        tgt_size = 14.0
        corner_l = 4.0
        tgt_rect = QRectF(dot_x - tgt_size, dot_y - tgt_size, tgt_size * 2, tgt_size * 2)
        pen_tgt = QPen(EvaTheme.NERV_RED if curr_g > 0.4 else EvaTheme.NERV_AMBER, 1.5)
        painter.setPen(pen_tgt)

        # 4 corners of tracking box
        painter.drawLine(int(tgt_rect.left()), int(tgt_rect.top() + corner_l), int(tgt_rect.left()), int(tgt_rect.top()))
        painter.drawLine(int(tgt_rect.left()), int(tgt_rect.top()), int(tgt_rect.left() + corner_l), int(tgt_rect.top()))
        painter.drawLine(int(tgt_rect.right() - corner_l), int(tgt_rect.top()), int(tgt_rect.right()), int(tgt_rect.top()))
        painter.drawLine(int(tgt_rect.right()), int(tgt_rect.top()), int(tgt_rect.right()), int(tgt_rect.top() + corner_l))
        painter.drawLine(int(tgt_rect.left()), int(tgt_rect.bottom() - corner_l), int(tgt_rect.left()), int(tgt_rect.bottom()))
        painter.drawLine(int(tgt_rect.left()), int(tgt_rect.bottom()), int(tgt_rect.left() + corner_l), int(tgt_rect.bottom()))
        painter.drawLine(int(tgt_rect.right() - corner_l), int(tgt_rect.bottom()), int(tgt_rect.right()), int(tgt_rect.bottom()))
        painter.drawLine(int(tgt_rect.right()), int(tgt_rect.bottom()), int(tgt_rect.right()), int(tgt_rect.bottom() - corner_l))

        # Center tracking dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(EvaTheme.NERV_RED if curr_g > 0.4 else EvaTheme.NERV_ORANGE))
        painter.drawEllipse(QPointF(dot_x, dot_y), 3.5, 3.5)
        painter.setBrush(Qt.NoBrush)

        # 6. Massive Pale-Cream Serif Speed Numerals: 108
        speed_val = int(round(self.telemetry.speed_kmh))
        speed_str = f"{speed_val}"

        painter.setFont(EvaTheme.get_serif_font(74, bold=True))
        painter.setPen(EvaTheme.EVA_YELLOW)
        speed_rect = QRectF(cx - 130, cy - 68, 260, 80)
        painter.drawText(speed_rect, Qt.AlignCenter, speed_str)

        # Unit: km/h
        painter.setFont(EvaTheme.get_serif_font(14, bold=True))
        painter.setPen(EvaTheme.EVA_YELLOW)
        unit_rect = QRectF(cx - 50, cy + 14, 100, 22)
        painter.drawText(unit_rect, Qt.AlignCenter, "km/h")

        # 7. Subtitle: G-FORCE LOCK-ON in Acid Green
        painter.setFont(EvaTheme.get_font(11, bold=True, mono=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        sub_rect = QRectF(cx - 120, cy + 42, 240, 22)
        painter.drawText(sub_rect, Qt.AlignCenter, "G-FORCE LOCK-ON")

        # 8. Bottom Tactical Mode Pill & Live Vector Readout
        is_ev = self.telemetry.drive_mode == "EV" or self.telemetry.engine_rpm == 0
        pill_w = 170.0
        pill_h = 22.0
        pill_rect = QRectF(cx - pill_w / 2.0, cy + radius * 0.65, pill_w, pill_h)

        if is_ev:
            pill_border = EvaTheme.EVA_GREEN
            pill_text = "⚡ INTERNAL BATTERY // EV"
        else:
            pill_border = EvaTheme.NERV_ORANGE
            pill_text = "⚙ UMBILICAL POWER // HYB"

        painter.setPen(QPen(pill_border, 1.2))
        painter.setBrush(QBrush(QColor(pill_border.red(), pill_border.green(), pill_border.blue(), 25)))
        painter.drawRect(pill_rect)

        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(pill_border)
        painter.drawText(pill_rect, Qt.AlignCenter, pill_text)

        # Live dual-axis G-Force readout
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED)
        g_axis_str = f"LAT: {self.telemetry.g_lat:+.2f}G   LON: {self.telemetry.g_long:+.2f}G   PEAK: {self.telemetry.g_peak:.2f}G"
        painter.drawText(QRectF(cx - 140, cy + radius * 0.76, 280, 18), Qt.AlignCenter, g_axis_str)
