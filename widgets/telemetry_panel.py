"""
Right Panel: Cyberpunk Engine & Electrical Telemetry Panel
Features:
- Chamfered tech frame with carbon fiber texture & tactical brackets
- Gradient filled oscilloscope area charts with scanning beam for Coolant & 12V Aux
- Tall segmented multi-color LED level meters for Throttle & Motor Power
- Peak hold indicator and dynamic color transitions (Cyan -> Amber -> Neon Red)
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QRectF
from themes.cyberpunk_theme import CyberTheme
from themes.eva_theme import EvaTheme
from core.telemetry import VehicleTelemetry


class TelemetryPanelWidget(QWidget):
    def __init__(self, parent=None, theme="eva"):
        super().__init__(parent)
        self.telemetry = VehicleTelemetry()
        self.scan_x = 0.0
        self.throttle_peak = 0.0
        self.motor_peak = 0.0
        self.theme = theme

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def update_telemetry(self, telemetry: VehicleTelemetry):
        self.telemetry = telemetry
        self.scan_x = (self.scan_x + 0.03) % 1.0

        # Peak hold with smooth decay
        if self.telemetry.throttle_pct >= self.throttle_peak:
            self.throttle_peak = self.telemetry.throttle_pct
        else:
            self.throttle_peak = max(self.telemetry.throttle_pct, self.throttle_peak - 0.3)

        disp_pwr = max(0.0, self.telemetry.motor_power_kw)
        if disp_pwr >= self.motor_peak:
            self.motor_peak = disp_pwr
        else:
            self.motor_peak = max(disp_pwr, self.motor_peak - 0.4)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        W, H = self.width(), self.height()

        if self.theme == "eva":
            self.draw_eva_concept_magi_honeycomb(painter, W, H)
            return

        is_eva = False

        # 1. Outer Frame with Chamfered Corners
        card_rect = QRectF(6, 6, W - 12, H - 12)
        if is_eva:
            EvaTheme.draw_nerv_frame(painter, card_rect, EvaTheme.NERV_ORANGE, corner_cut=12.0)
        else:
            CyberTheme.draw_tech_frame(painter, card_rect, CyberTheme.BG_CARD_BORDER, corner_cut=12.0)
            CyberTheme.draw_carbon_pattern(painter, card_rect)

        # 2. Header Title with Channel Badge
        if is_eva:
            painter.setFont(EvaTheme.get_font(12, bold=True))
            painter.setPen(EvaTheme.NERV_ORANGE)
            painter.drawText(22, 34, "MAGI TELEMETRY")

            painter.setFont(EvaTheme.get_font(9, bold=True, mono=True))
            painter.setPen(EvaTheme.NERV_AMBER)
            painter.drawText(int(W - 85), 34, "// MAGI-01")

            # Bold NERV hazard stripe bar across panel header
            EvaTheme.draw_hazard_stripes(painter, QRectF(22, 41, W - 44, 4), stripe_color=EvaTheme.NERV_ORANGE, stripe_width=4, step=8, border=False)
        else:
            painter.setFont(CyberTheme.get_font(12, bold=True))
            painter.setPen(CyberTheme.CYAN_BRIGHT)
            painter.drawText(22, 34, "VEHICLE TELEMETRY")

            painter.setFont(CyberTheme.get_font(9, bold=True, mono=True))
            painter.setPen(CyberTheme.TEXT_MUTED)
            painter.drawText(int(W - 85), 34, "// CH-02")

        # Top section: Two Waveform Monitors (Coolant Temp & 12V Aux Battery)
        box_w = W - 44
        box_h = 50
        x = 22

        # 3. Engine Coolant Monitor: "ENG TEMP: 88°C"
        y1 = 44
        font_hdr = EvaTheme.get_font(11, bold=True) if is_eva else CyberTheme.get_font(11, bold=True)
        font_sub = EvaTheme.get_font(8, bold=True, mono=True) if is_eva else CyberTheme.get_font(8, bold=True, mono=True)
        text_white = EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE
        text_muted = EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED

        painter.setFont(font_hdr)
        painter.setPen(text_white)
        painter.drawText(x, y1 + 16, f"ENG TEMP: {self.telemetry.coolant_temp_c}°C")

        c_min = min(self.telemetry.coolant_history) if self.telemetry.coolant_history else 80
        c_max = max(self.telemetry.coolant_history) if self.telemetry.coolant_history else 90
        painter.setFont(font_sub)
        painter.setPen(text_muted)
        painter.drawText(int(x + box_w - 95), y1 + 16, f"HI:{int(c_max)}° LO:{int(c_min)}°")

        coolant_color = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_CORE
        self.draw_oscilloscope_chart(painter, x, y1 + 24, box_w, box_h,
                                     self.telemetry.coolant_history, coolant_color, 60.0, 110.0)

        # 4. 12V Aux Battery Monitor: "AUX BATT: 14.1V"
        y2 = y1 + 84
        painter.setFont(font_hdr)
        painter.setPen(text_white)
        painter.drawText(x, y2 + 16, f"AUX BATT: {self.telemetry.aux_voltage:.1f}V")

        a_min = min(self.telemetry.aux_history) if self.telemetry.aux_history else 13.8
        a_max = max(self.telemetry.aux_history) if self.telemetry.aux_history else 14.3
        painter.setFont(font_sub)
        painter.setPen(text_muted)
        painter.drawText(int(x + box_w - 95), y2 + 16, f"HI:{a_max:.1f} LO:{a_min:.1f}")

        aux_color = EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_CORE
        self.draw_oscilloscope_chart(painter, x, y2 + 24, box_w, box_h,
                                     self.telemetry.aux_history, aux_color, 11.5, 15.0)

        # 5. Bottom Section: Dual Vertical Segmented Slanted LED Level Meters (Throttle & Motor Power)
        if is_eva:
            # Tactical EVA hazard stripe divider banner
            divider_rect = QRectF(x, y2 + 76, box_w, 12)
            EvaTheme.draw_hazard_badge(painter, divider_rect, "MAGI-01 DRIVE POWER", text_color=EvaTheme.NERV_AMBER, stripe_color=EvaTheme.NERV_ORANGE, font_size=6)

        bar_area_y = y2 + 104
        bar_area_h = H - bar_area_y - 14
        col_w = (box_w - 24) / 2.0

        # Segmented Throttle Position Bar with Peak Hold
        throt_x = x + 4
        throt_base = EvaTheme.NERV_AMBER if is_eva else CyberTheme.AMBER_CORE
        self.draw_segmented_meter(
            painter, throt_x, bar_area_y, col_w, bar_area_h,
            value=self.telemetry.throttle_pct, max_val=100.0,
            peak_val=self.throttle_peak,
            label="THROTTLE", unit=f"{int(self.telemetry.throttle_pct)}%",
            base_color=throt_base, is_throttle=True
        )

        # Segmented Motor Power Bar with Peak Hold
        motor_x = x + col_w + 20
        disp_power = max(0.0, self.telemetry.motor_power_kw)
        motor_base = EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_CORE
        self.draw_segmented_meter(
            painter, motor_x, bar_area_y, col_w, bar_area_h,
            value=disp_power, max_val=135.0,
            peak_val=self.motor_peak,
            label="MOTOR PWR", unit=f"{int(disp_power)}kW",
            base_color=motor_base, is_throttle=False
        )

    def draw_oscilloscope_chart(self, painter, x, y, w, h, data, line_color, min_val, max_val):
        """Draws high-tech oscilloscope with gradient-filled area and sweep beam."""
        is_eva = self.theme == "eva"
        box = QRectF(x, y, w, h)
        grid_b = EvaTheme.GRID_LINE_BRIGHT if is_eva else CyberTheme.GRID_LINE_BRIGHT
        painter.setPen(QPen(grid_b, 1))
        painter.setBrush(QBrush(QColor(10, 12, 18, 220)))
        painter.drawRect(box)

        # Grid divisions
        grid_l = EvaTheme.GRID_LINE if is_eva else CyberTheme.GRID_LINE
        painter.setPen(QPen(grid_l, 1, Qt.DotLine))
        for i in range(1, 4):
            gx = x + (w / 4) * i
            painter.drawLine(int(gx), int(y), int(gx), int(y + h))
        painter.drawLine(int(x), int(y + h / 2), int(x + w), int(y + h / 2))

        # Sweep beam line
        sweep_pos_x = x + self.scan_x * w
        sweep_c = QColor(255, 102, 0, 45) if is_eva else QColor(0, 240, 255, 45)
        painter.setPen(QPen(sweep_c, 1.5))
        painter.drawLine(int(sweep_pos_x), int(y), int(sweep_pos_x), int(y + h))

        if not data or len(data) < 2:
            return

        path = QPainterPath()
        area_path = QPainterPath()
        span = max(1.0, max_val - min_val)
        step_x = w / (len(data) - 1)

        area_path.moveTo(x, y + h)

        for idx, val in enumerate(data):
            norm = (val - min_val) / span
            norm = max(0.0, min(1.0, norm))
            px = x + idx * step_x
            py = y + h - (norm * (h - 8)) - 4
            if idx == 0:
                path.moveTo(px, py)
                area_path.lineTo(px, py)
            else:
                path.lineTo(px, py)
                area_path.lineTo(px, py)

        area_path.lineTo(x + w, y + h)
        area_path.closeSubpath()

        # Gradient area fill
        area_grad = QLinearGradient(x, y, x, y + h)
        c_fill = QColor(line_color)
        c_fill.setAlpha(45)
        area_grad.setColorAt(0.0, c_fill)
        area_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(area_grad))
        painter.drawPath(area_path)

        # Waveform line
        if is_eva:
            painter.setPen(QPen(line_color, 1.8))
            painter.drawPath(path)
        else:
            CyberTheme.draw_neon_path(painter, path, line_color, core_width=1.8, glow_passes=2)

    def draw_segmented_meter(self, painter, x, y, w, h, value, max_val, peak_val, label, unit, base_color, is_throttle):
        """Draws discrete slanted LED segment blocks with floating peak marker."""
        is_eva = self.theme == "eva"
        meter_h = h - 45
        num_segments = 18
        seg_h = (meter_h - (num_segments * 2)) / num_segments
        pct = max(0.0, min(1.0, value / max_val))
        active_count = int(round(pct * num_segments))

        peak_pct = max(0.0, min(1.0, peak_val / max_val))
        peak_idx = int(round(peak_pct * num_segments)) - 1

        font_label = EvaTheme.get_font(9, bold=True) if is_eva else CyberTheme.get_font(9, bold=True)
        font_unit = EvaTheme.get_font(10, bold=True, mono=True) if is_eva else CyberTheme.get_font(10, bold=True, mono=True)
        font_tick = EvaTheme.get_font(6, bold=True, mono=True) if is_eva else CyberTheme.get_font(6, bold=True, mono=True)
        text_muted = EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED

        # Title & Value at top of bar
        painter.setFont(font_label)
        painter.setPen(text_muted)
        painter.drawText(int(x), int(y - 4), label)

        painter.setFont(font_unit)
        painter.setPen(base_color)
        painter.drawText(int(x + w - 48), int(y - 4), unit)

        slant = 4.0

        # Side graduation tick marks
        painter.setFont(font_tick)
        painter.setPen(text_muted)
        for pct_step in (0.0, 0.25, 0.5, 0.75, 1.0):
            tick_y = y + meter_h - (pct_step * meter_h)
            if is_throttle:
                painter.drawLine(int(x - 4), int(tick_y), int(x - 1), int(tick_y))
            else:
                painter.drawLine(int(x + w + 1), int(tick_y), int(x + w + 4), int(tick_y))

        # Draw Segments from bottom to top
        for i in range(num_segments):
            seg_y = y + meter_h - ((i + 1) * (seg_h + 2))
            seg_rect = QRectF(x, seg_y, w, seg_h)

            if i < active_count:
                # Color staging (Eco / Med / High)
                if is_eva:
                    if is_throttle:
                        if i > num_segments * 0.8:
                            c = EvaTheme.NERV_RED
                        elif i > num_segments * 0.5:
                            c = EvaTheme.NERV_ORANGE
                        else:
                            c = EvaTheme.ACID_GREEN
                    else:
                        if i > num_segments * 0.8:
                            c = EvaTheme.NERV_RED
                        elif i > num_segments * 0.5:
                            c = EvaTheme.NERV_ORANGE
                        else:
                            c = EvaTheme.ACID_GREEN
                else:
                    if is_throttle:
                        if i > num_segments * 0.8:
                            c = CyberTheme.NEON_RED
                        elif i > num_segments * 0.5:
                            c = CyberTheme.AMBER_CORE
                        else:
                            c = CyberTheme.CYAN_CORE
                    else:
                        c = CyberTheme.CYAN_CORE if i <= num_segments * 0.75 else CyberTheme.ELECTRIC_BLUE

                CyberTheme.draw_slanted_rect(painter, seg_rect, slant_dx=slant, fill_color=c)

                # Glow highlight for top active segment
                if i == active_count - 1:
                    top_highlight = EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE
                    CyberTheme.draw_slanted_rect(painter, seg_rect, slant_dx=slant, fill_color=top_highlight)
            else:
                dim_c = QColor(14, 16, 24, 180)
                CyberTheme.draw_slanted_rect(painter, seg_rect, slant_dx=slant, fill_color=dim_c)

            # Draw floating Peak Hold marker
            if i == peak_idx and peak_idx > active_count - 1:
                if is_eva:
                    peak_c = EvaTheme.NERV_RED if is_throttle else EvaTheme.NERV_AMBER
                else:
                    peak_c = CyberTheme.NEON_RED if is_throttle else CyberTheme.CYAN_BRIGHT
                CyberTheme.draw_slanted_rect(painter, seg_rect, slant_dx=slant, border_color=peak_c, fill_color=peak_c)

    def draw_eva_concept_magi_honeycomb(self, painter, W, H):
        """
        Renders the authentic Evangelion MAGI Hexagonal Honeycomb Matrix (六角蜂巢矩陣):
        - Top Cluster: COOLANT TEMP 89°C, ENG RPM 1250 / 106%, AUX BATT 14.3V
        - Mid Cluster: THROTTLE 35%, SYSTEM OUTPUT 28kW
        - Middle Dual Slanted Segmented LED Power Meters:
          * POWER OUTPUT / LOWER
          * MQBITER / POWER
        - Bottom Cluster:
          * IPU VOLT 178V, POWER OUTPUT 73.0 kW, IPU TEMP 25°C
          * DIAGNOSTIC 53.0 電流, DRIVE MODE EV MODE, VHG.ASIS 43.0 km/h
        """
        # 1. Outer Frame
        card_rect = QRectF(6, 6, W - 12, H - 12)
        painter.fillRect(card_rect, QColor(8, 6, 14, 250))
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 2.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(card_rect)

        # 2. Header Title & Top Hazard Bar
        EvaTheme.draw_hazard_stripes(painter, QRectF(12, 10, W - 24, 4),
                                     stripe_color=EvaTheme.NERV_ORANGE, stripe_width=4, step=8, border=False)

        painter.setFont(EvaTheme.get_serif_font(14, bold=True))
        painter.setPen(EvaTheme.NERV_AMBER)
        painter.drawText(16, 29, "MAGI TELEMETRY")

        painter.setFont(EvaTheme.get_font(10, bold=True, mono=True))
        painter.setPen(EvaTheme.NERV_ORANGE)
        painter.drawText(int(W - 95), 29, "// MAGI-01")

        # 3. Hexagon Cluster Geometry
        cx = W / 2.0
        # Adaptively scale hexagon radius (enlarged to 52px for 720p)
        r = min(54.0, max(48.0, 52.0 * min(W / 365.0, H / 616.0)))
        dx = 1.73205 * r        # ≈ 90.07px
        dx_half = dx / 2.0      # ≈ 45.03px
        dy = 1.5 * r            # ≈ 78.00px

        # Calculate proportional vertical offsets to utilize entire panel height
        extra_h = max(0.0, H - 616.0)

        # ==========================================
        # TOP CLUSTER (Row 1: 3 hexes, Row 2: 2 hexes)
        # ==========================================
        cy1 = 94.0 + extra_h * 0.1

        # Hex 1 (Top Left): Coolant Temp
        self.draw_magi_hex(
            painter, cx - dx, cy1, r,
            border_color=EvaTheme.HEX_PURPLE,
            title="COOLANT TEMP",
            value=f"{self.telemetry.coolant_temp_c}°C",
            footer="ENG STATUS",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Hex 2 (Top Center): Engine RPM
        rpm_val = self.telemetry.engine_rpm
        rpm_str = f"{rpm_val}" if rpm_val > 0 else "OFF"
        rpm_pct = f"{int(rpm_val / 6000.0 * 100)}%" if rpm_val > 0 else "EV STANDBY"
        self.draw_magi_hex(
            painter, cx, cy1, r,
            border_color=EvaTheme.HEX_AMBER,
            title="ENG RPM",
            value=rpm_str,
            footer=rpm_pct,
            val_color=EvaTheme.NERV_AMBER if rpm_val > 0 else EvaTheme.EVA_GREEN
        )

        # Hex 3 (Top Right): 12V Aux Battery
        self.draw_magi_hex(
            painter, cx + dx, cy1, r,
            border_color=EvaTheme.HEX_AMBER,
            title="AUX BATT",
            value=f"{self.telemetry.aux_voltage:.1f}V",
            footer="14.3V NORM",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Row 2 (Mid Left & Mid Right nestled between Row 1)
        cy2 = cy1 + dy  # ≈ 172.0px

        # Hex 4 (Mid Left): Throttle
        self.draw_magi_hex(
            painter, cx - dx_half, cy2, r,
            border_color=EvaTheme.HEX_PURPLE,
            title="THROTTLE",
            value=f"{int(self.telemetry.throttle_pct)}%",
            footer="POS. REQ",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Hex 5 (Mid Right): System Output
        disp_pwr = int(abs(self.telemetry.motor_power_kw))
        pwr_status = "REGEN" if self.telemetry.motor_power_kw < -1.0 else "NOMINAL"
        pwr_col = EvaTheme.EVA_GREEN if self.telemetry.motor_power_kw < -1.0 else EvaTheme.EVA_YELLOW
        self.draw_magi_hex(
            painter, cx + dx_half, cy2, r,
            border_color=EvaTheme.HEX_PURPLE,
            title="SYSTEM OUTPUT",
            value=f"{disp_pwr}kW",
            footer=pwr_status,
            val_color=pwr_col
        )

        # ==========================================
        # MIDDLE HORIZONTAL SEGMENTED LED METERS
        # ==========================================
        m_x = 16
        m_w = W - 32
        m_y1 = int(cy2 + r * 0.95 + extra_h * 0.15)  # ≈ 246px
        pwr_norm = min(1.0, max(0.0, self.telemetry.motor_power_kw / 120.0))
        self.draw_horizontal_segmented_meter(
            painter, m_x, m_y1, m_w, 19,
            label="POWER OUTPUT / LOWER",
            value_norm=pwr_norm,
            col_start=EvaTheme.EVA_GREEN,
            col_end=EvaTheme.NERV_ORANGE
        )

        m_y2 = m_y1 + 26  # ≈ 272px
        throt_norm = min(1.0, max(0.0, self.telemetry.throttle_pct / 100.0))
        self.draw_horizontal_segmented_meter(
            painter, m_x, m_y2, m_w, 19,
            label="MQBITER / POWER",
            value_norm=throt_norm,
            col_start=EvaTheme.NERV_AMBER,
            col_end=EvaTheme.NERV_RED
        )

        # ==========================================
        # BOTTOM CLUSTER (Row 3, 4, 5)
        # ==========================================
        cy3 = int(m_y2 + r + 24 + extra_h * 0.3)  # ≈ 356px

        # Hex 6 (Lower Left): IPU Voltage
        self.draw_magi_hex(
            painter, cx - dx, cy3, r,
            border_color=EvaTheme.HEX_AMBER,
            title="IPU VOLT",
            value=f"{self.telemetry.battery_voltage_v:.0f}V",
            footer="HIGH VOLT",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Hex 7 (Lower Center): Power Output
        curr_pwr = max(0.0, self.telemetry.motor_power_kw)
        self.draw_magi_hex(
            painter, cx, cy3, r,
            border_color=EvaTheme.HEX_PURPLE,
            title="POWER OUTPUT",
            value=f"{curr_pwr:.1f}",
            footer="kW MOTOR",
            val_color=EvaTheme.EVA_GREEN
        )

        # Hex 8 (Lower Right): IPU Temp
        self.draw_magi_hex(
            painter, cx + dx, cy3, r,
            border_color=EvaTheme.HEX_AMBER,
            title="IPU TEMP",
            value=f"{self.telemetry.battery_temp_c}°C",
            footer="THERMAL OK",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Row 4 (Bottom Mid-Left & Mid-Right)
        cy4 = cy3 + dy  # ≈ 434px

        # Hex 9 (Bottom Left): Diagnostic Current
        curr_amp = abs(self.telemetry.motor_power_kw * 1000 / max(1.0, self.telemetry.battery_voltage_v))
        self.draw_magi_hex(
            painter, cx - dx_half, cy4, r,
            border_color=EvaTheme.HEX_PURPLE,
            title="DIAGNOSTIC",
            value=f"{curr_amp:.1f}",
            footer="53A 電流",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Hex 10 (Bottom Right): Drive Mode
        is_ev = self.telemetry.drive_mode == "EV" or self.telemetry.engine_rpm == 0
        self.draw_magi_hex(
            painter, cx + dx_half, cy4, r,
            border_color=EvaTheme.HEX_AMBER if is_ev else EvaTheme.HEX_PURPLE,
            title="DRIVE MODE",
            value="EV MODE" if is_ev else "HYBRID",
            footer="SYNC ACTIVE",
            val_color=EvaTheme.EVA_GREEN if is_ev else EvaTheme.NERV_ORANGE
        )

        # Row 5 (Bottom Anchor Hexagon: Vehicle Speed / Assist)
        cy5 = cy4 + dy  # ≈ 512px
        self.draw_magi_hex(
            painter, cx, cy5, r,
            border_color=EvaTheme.HEX_AMBER,
            title="VHG.ASIS",
            value=f"{self.telemetry.speed_kmh:.1f}",
            footer="km/h SPEED",
            val_color=EvaTheme.EVA_YELLOW
        )

        # Tactical Bottom Status Pill
        pill_y = cy5 + r * 0.92
        if pill_y + 24 <= H - 6:
            pill_rect = QRectF(16, pill_y, W - 32, 24)
            EvaTheme.draw_hazard_badge(painter, pill_rect, "MAGI SYSTEM NOMINAL",
                                       text_color=EvaTheme.NERV_AMBER, stripe_color=EvaTheme.NERV_ORANGE, font_size=8.5)

    def draw_magi_hex(self, painter, cx, cy, r, border_color, title, value, footer, val_color=None):
        """Draws single pointy-topped MAGI hexagon cell with title, serif value, and footer."""
        EvaTheme.draw_pointy_hexagon(painter, cx, cy, r, border_color, fill_color=EvaTheme.HEX_BG, line_width=1.8)

        # Top Title (enlarged to 8pt)
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED)
        title_rect = QRectF(cx - r * 0.85, cy - r * 0.68, r * 1.7, 16)
        painter.drawText(title_rect, Qt.AlignCenter, title)

        # Center Serif Value (enlarged to 14-18pt)
        val_font_size = 14 if len(value) >= 6 else (16 if len(value) >= 5 else 18)
        painter.setFont(EvaTheme.get_serif_font(val_font_size, bold=True))
        painter.setPen(val_color or EvaTheme.EVA_YELLOW)
        val_rect = QRectF(cx - r * 0.92, cy - 13, r * 1.84, 28)
        painter.drawText(val_rect, Qt.AlignCenter, value)

        # Bottom Footer (enlarged to 8pt)
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.NERV_AMBER)
        foot_rect = QRectF(cx - r * 0.85, cy + r * 0.36, r * 1.7, 16)
        painter.drawText(foot_rect, Qt.AlignCenter, footer)

    def draw_horizontal_segmented_meter(self, painter, x, y, w, h, label, value_norm, col_start, col_end):
        """Draws discrete slanted multi-color LED segments for MAGI power meter."""
        # Label on left (enlarged to 8.5pt bold)
        label_w = 135
        painter.setFont(EvaTheme.get_font(8.5, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED)
        painter.drawText(QRectF(x, y, label_w, h), Qt.AlignVCenter | Qt.AlignLeft, label)

        # Segments on right
        bar_x = x + label_w + 6
        bar_w = w - label_w - 6
        num_segs = 16
        gap = 2.5
        seg_w = max(2.0, (bar_w - (num_segs - 1) * gap) / float(num_segs))
        active_count = int(round(max(0.0, min(1.0, value_norm)) * num_segs))

        for i in range(num_segs):
            sx = bar_x + i * (seg_w + gap)
            seg_rect = QRectF(sx, y + 1, seg_w, h - 2)

            if i < active_count:
                t = i / float(max(1, num_segs - 1))
                r = int(col_start.red() + t * (col_end.red() - col_start.red()))
                g = int(col_start.green() + t * (col_end.green() - col_start.green()))
                b = int(col_start.blue() + t * (col_end.blue() - col_start.blue()))
                CyberTheme.draw_slanted_rect(painter, seg_rect, slant_dx=3.0, fill_color=QColor(r, g, b))
            else:
                CyberTheme.draw_slanted_rect(painter, seg_rect, slant_dx=3.0, fill_color=QColor(16, 12, 24, 200))
