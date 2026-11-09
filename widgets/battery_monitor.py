"""
Left Panel: Hybrid Battery Monitor & 2D Animated Copilot
Supports dual themes:
- "eva": Neon Genesis Evangelion / Rei Ayanami Entry Plug Cockpit
- "cyberpunk": High-tech Blue/Cyan Cyberpunk Cockpit
"""

import os
import math
import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient, QPixmap, QPolygonF
)
from PyQt5.QtCore import Qt, QPointF, QRectF
from themes.cyberpunk_theme import CyberTheme
from themes.eva_theme import EvaTheme
from core.telemetry import VehicleTelemetry


class Particle:
    def __init__(self, segment=0):
        self.segment = segment  # 0: Battery -> Motor, 1: Motor -> Engine
        self.progress = random.random()
        self.speed = 0.016 + random.random() * 0.012
        self.size = 2.5 + random.random() * 2.0


class BatteryMonitorWidget(QWidget):
    def __init__(self, parent=None, theme="eva"):
        super().__init__(parent)
        self.telemetry = VehicleTelemetry()
        self.particles = [Particle(segment=i % 2) for i in range(40)]
        self.scan_x = 0.0
        self.anim_tick = 0
        self.theme = theme

        # Load & prepare Avatar Pixmap
        self.rq_pixmap = None
        self._init_race_queen_asset()

    def set_theme(self, theme: str):
        self.theme = theme
        self._init_race_queen_asset()
        self.update()

    def _init_race_queen_asset(self):
        """Loads and crops the cyber or EVA Rei avatar into memory."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if self.theme == "eva":
            cropped_path = os.path.join(base_dir, "eva_rei_cropped.jpg")
            raw_path = os.path.join(base_dir, "eva_rei.jpg")
            if os.path.exists(cropped_path):
                self.rq_pixmap = QPixmap(cropped_path)
            elif os.path.exists(raw_path):
                raw_pix = QPixmap(raw_path)
                if not raw_pix.isNull():
                    w, h = raw_pix.width(), raw_pix.height()
                    crop_rect = QRectF(w * 0.09, h * 0.08, w * 0.82, h * 0.63)
                    cropped = raw_pix.copy(crop_rect.toRect())
                    cropped.save(cropped_path)
                    self.rq_pixmap = cropped
                else:
                    self.rq_pixmap = raw_pix
            else:
                self.rq_pixmap = None
        else:
            cropped_path = os.path.join(base_dir, "cyber_race_queen_cropped.jpg")
            raw_path = os.path.join(base_dir, "cyber_race_queen.jpg")
            if os.path.exists(cropped_path):
                self.rq_pixmap = QPixmap(cropped_path)
            elif os.path.exists(raw_path):
                raw_pix = QPixmap(raw_path)
                if not raw_pix.isNull():
                    w, h = raw_pix.width(), raw_pix.height()
                    crop_rect = QRectF(w * 0.09, h * 0.04, w * 0.82, h * 0.67)
                    cropped = raw_pix.copy(crop_rect.toRect())
                    cropped.save(cropped_path)
                    self.rq_pixmap = cropped
                else:
                    self.rq_pixmap = raw_pix
            else:
                self.rq_pixmap = None

    def update_telemetry(self, telemetry: VehicleTelemetry):
        self.telemetry = telemetry
        is_regen = self.telemetry.drive_mode == "REGEN" or self.telemetry.motor_power_kw < -2.0
        speed_mult = 1.8 if abs(self.telemetry.motor_power_kw) > 40 else 1.0

        # Update flowing particles
        for p in self.particles:
            step = p.speed * speed_mult
            if is_regen:
                p.progress -= step
                if p.progress < 0.0:
                    p.progress = 1.0
            else:
                p.progress += step
                if p.progress > 1.0:
                    p.progress = 0.0

        # Oscilloscope scan beam animation & tick
        self.scan_x = (self.scan_x + 0.03) % 1.0
        self.anim_tick += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        W, H = self.width(), self.height()

        if self.theme == "eva":
            self.draw_eva_concept_panel(painter, W, H)
            return

        is_eva = False

        # Cyberpunk Theme
        card_rect = QRectF(6, 6, W - 12, H - 12)
        CyberTheme.draw_tech_frame(painter, card_rect, CyberTheme.BG_CARD_BORDER, corner_cut=12.0)
        CyberTheme.draw_carbon_pattern(painter, card_rect)

        # Header Title
        painter.setFont(CyberTheme.get_font(12, bold=True))
        painter.setPen(CyberTheme.CYAN_BRIGHT)
        painter.drawText(22, 34, "HYBRID BATTERY MONITOR")

        painter.setFont(CyberTheme.get_font(9, bold=True, mono=True))
        painter.setPen(CyberTheme.TEXT_MUTED)
        painter.drawText(int(W - 85), 34, "// IPU-CORE")

        # 3. Leftmost Tall Vertical Battery Gauge
        batt_x, batt_y = 28, 62
        batt_w, batt_h = 44, H - 162
        cap_h = 8
        cap_w = 18

        # Battery Graduation Marks (0, 25, 50, 75, 100%)
        mark_font = EvaTheme.get_font(7, bold=True, mono=True) if is_eva else CyberTheme.get_font(7, bold=True, mono=True)
        mark_color = EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED
        painter.setFont(mark_font)
        painter.setPen(mark_color)
        for pct_mark in (0, 25, 50, 75, 100):
            mark_y = batt_y + batt_h - 4 - (batt_h - 8) * (pct_mark / 100.0)
            painter.drawLine(int(batt_x - 5), int(mark_y), int(batt_x), int(mark_y))

        # Battery Top Terminal Cap
        cap_rect = QRectF(batt_x + (batt_w - cap_w) / 2, batt_y - cap_h + 1, cap_w, cap_h)
        if is_eva:
            EvaTheme.draw_hazard_stripes(painter, cap_rect, stripe_color=EvaTheme.NERV_ORANGE, stripe_width=3, step=6, border=True)
        else:
            cap_border = CyberTheme.CYAN_DIM
            cap_bg = CyberTheme.BG_CARD
            painter.setPen(QPen(cap_border, 1.5))
            painter.setBrush(QBrush(cap_bg))
            painter.drawRoundedRect(cap_rect, 2, 2)

        # Battery Main Frame
        body_rect = QRectF(batt_x, batt_y, batt_w, batt_h)
        body_border = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_CORE
        painter.setPen(QPen(body_border, 2))
        painter.setBrush(QBrush(QColor(8, 10, 16, 230)))
        painter.drawRoundedRect(body_rect, 6, 6)

        # Battery Liquid Fill (SoC %)
        soc = max(0.0, min(100.0, self.telemetry.battery_soc_pct))
        fill_h = (batt_h - 8) * (soc / 100.0)
        fill_y = batt_y + batt_h - 4 - fill_h

        if fill_h > 4:
            fill_rect = QRectF(batt_x + 4, fill_y, batt_w - 8, fill_h)
            fill_grad = QLinearGradient(batt_x, fill_y, batt_x + batt_w, fill_y + fill_h)
            if is_eva:
                fill_grad.setColorAt(0.0, EvaTheme.ACID_GREEN)
                fill_grad.setColorAt(0.4, EvaTheme.NERV_AMBER)
                fill_grad.setColorAt(1.0, EvaTheme.NERV_ORANGE)
            else:
                fill_grad.setColorAt(0.0, CyberTheme.CYAN_BRIGHT)
                fill_grad.setColorAt(0.2, CyberTheme.CYAN_CORE)
                fill_grad.setColorAt(1.0, CyberTheme.ELECTRIC_BLUE)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(fill_grad))
            painter.drawRoundedRect(fill_rect, 4, 4)

            # Glowing Meniscus line on liquid top
            painter.setPen(QPen(EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE, 2.5))
            painter.drawLine(int(batt_x + 6), int(fill_y + 1), int(batt_x + batt_w - 6), int(fill_y + 1))

        # Battery internal cell partitions
        for c_idx in range(1, 10):
            cy_div = batt_y + (batt_h / 10.0) * c_idx
            painter.setPen(QPen(QColor(0, 0, 0, 130), 1.2))
            painter.drawLine(int(batt_x + 3), int(cy_div), int(batt_x + batt_w - 3), int(cy_div))

        # Glass Specular Highlight Reflection
        glass_sheen = QRectF(batt_x + batt_w - 9, batt_y + 4, 5, batt_h - 8)
        sheen_grad = QLinearGradient(glass_sheen.x(), glass_sheen.y(), glass_sheen.x() + glass_sheen.width(), glass_sheen.y())
        sheen_grad.setColorAt(0.0, QColor(255, 255, 255, 20))
        sheen_grad.setColorAt(1.0, QColor(255, 255, 255, 80))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(sheen_grad))
        painter.drawRoundedRect(glass_sheen, 2, 2)

        # Vertical Text: "INTERNAL BATTERY: 78%" or "STATE OF CHARGE: 78%"
        painter.save()
        painter.translate(batt_x - 8, batt_y + batt_h - 10)
        painter.rotate(-90)
        painter.setFont(EvaTheme.get_font(10, bold=True, mono=True) if is_eva else CyberTheme.get_font(11, bold=True, mono=True))
        painter.setPen(EvaTheme.NERV_AMBER if is_eva else CyberTheme.TEXT_WHITE)
        if is_eva:
            is_ev = self.telemetry.drive_mode == "EV"
            batt_text = f"INTERNAL: 04:59 [{int(soc)}%]" if is_ev else f"UMBILICAL: CONNECTED [{int(soc)}%]"
        else:
            batt_text = f"STATE OF CHARGE: {int(soc)}%"
        painter.drawText(0, 0, batt_text)
        painter.restore()

        # 4. Right side of Left Panel: Waveform Charts & 2D Race Queen Chamber
        chart_x = batt_x + batt_w + 24
        chart_w = W - chart_x - 20
        chart_h = 46

        # 4.1 Voltage Oscilloscope Chart
        v_y = 54
        painter.setFont(EvaTheme.get_font(10, bold=True) if is_eva else CyberTheme.get_font(10, bold=True))
        painter.setPen(EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE)
        painter.drawText(chart_x, v_y + 14, f"VOLTAGE: {self.telemetry.battery_voltage_v:.0f}V")

        v_min = min(self.telemetry.voltage_history) if self.telemetry.voltage_history else 170
        v_max = max(self.telemetry.voltage_history) if self.telemetry.voltage_history else 185
        painter.setFont(EvaTheme.get_font(7, bold=True, mono=True) if is_eva else CyberTheme.get_font(7, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED)
        painter.drawText(int(chart_x + chart_w - 85), v_y + 14, f"HI:{int(v_max)}V LO:{int(v_min)}V")

        v_color = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_CORE
        self.draw_oscilloscope_chart(painter, chart_x, v_y + 20, chart_w, chart_h,
                                     self.telemetry.voltage_history, v_color, 160.0, 190.0)

        # 4.2 Temperature Oscilloscope Chart
        t_y = v_y + 74
        painter.setFont(EvaTheme.get_font(10, bold=True) if is_eva else CyberTheme.get_font(10, bold=True))
        painter.setPen(EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE)
        painter.drawText(chart_x, t_y + 14, f"TEMP: {self.telemetry.battery_temp_c}°C")

        t_min = min(self.telemetry.batt_temp_history) if self.telemetry.batt_temp_history else 22
        t_max = max(self.telemetry.batt_temp_history) if self.telemetry.batt_temp_history else 28
        painter.setFont(EvaTheme.get_font(7, bold=True, mono=True) if is_eva else CyberTheme.get_font(7, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_MUTED if is_eva else CyberTheme.TEXT_MUTED)
        painter.drawText(int(chart_x + chart_w - 85), t_y + 14, f"HI:{int(t_max)}° LO:{int(t_min)}°")

        t_color = EvaTheme.LCL_CYAN if is_eva else CyberTheme.ELECTRIC_BLUE
        self.draw_oscilloscope_chart(painter, chart_x, t_y + 20, chart_w, chart_h,
                                     self.telemetry.batt_temp_history, t_color, 15.0, 45.0)

        # Sub-bar
        sub_bar_y = t_y + chart_h + 28
        painter.setFont(EvaTheme.get_font(7, bold=True, mono=True) if is_eva else CyberTheme.get_font(7, bold=True, mono=True))
        painter.setPen(EvaTheme.NERV_AMBER if is_eva else CyberTheme.CYAN_DIM)
        sub_label = "LCL STATUS: PURIFIED | SYNCHRO: 94.8%" if is_eva else "CELL: 3.72V AVG  |  SoH: 99.4%"
        painter.drawText(chart_x, sub_bar_y, sub_label)

        # 5. Middle: 2D Virtual Avatar Holographic Chamber
        rq_y = sub_bar_y + 10
        rq_h = H - rq_y - 94
        self.draw_race_queen_chamber(painter, chart_x, rq_y, chart_w, rq_h)

        # 6. Bottom Schematic Energy Flow (Battery ⇄ Motor ⇄ Engine)
        flow_y = H - 85
        self.draw_energy_flow_diagram(painter, 20, flow_y, W - 40, 75)

    def draw_race_queen_chamber(self, painter, x, y, w, h):
        """Draws the animated 2D holographic virtual Avatar / Rei Ayanami chamber."""
        is_eva = self.theme == "eva"
        # 1. Chamber Frame
        frame_rect = QRectF(x, y, w, h)
        if is_eva:
            EvaTheme.draw_nerv_frame(painter, frame_rect, EvaTheme.NERV_ORANGE, corner_cut=6.0)
        else:
            CyberTheme.draw_tech_frame(painter, frame_rect, CyberTheme.BG_CARD_BORDER, corner_cut=6.0)

        # Header bar
        if is_eva:
            # Bold NERV hazard badge header for Rei's cockpit
            badge_rect = QRectF(x, y, w, 18)
            EvaTheme.draw_hazard_badge(painter, badge_rect, "PILOT: AYANAMI REI", text_color=EvaTheme.NERV_ORANGE, font_size=7)

            pulse_alpha = int(180 + 75 * math.sin(self.anim_tick * 0.12))
            pulse_color = QColor(EvaTheme.ACID_GREEN)
            pulse_color.setAlpha(pulse_alpha)
            painter.setFont(EvaTheme.get_font(6, bold=True, mono=True))
            painter.setPen(pulse_color)
            painter.drawText(int(x + w - 48), int(y + 12), "● 100%")
        else:
            header_font = CyberTheme.get_font(7, bold=True, mono=True)
            painter.setFont(header_font)
            painter.setPen(CyberTheme.CYAN_BRIGHT)
            chamber_title = "// AI COPILOT // REI"
            painter.drawText(int(x + 8), int(y + 14), chamber_title)

            pulse_alpha = int(180 + 75 * math.sin(self.anim_tick * 0.12))
            pulse_color = QColor(CyberTheme.NEON_GREEN)
            pulse_color.setAlpha(pulse_alpha)
            painter.setPen(pulse_color)
            sync_label = "● ONLINE"
            painter.drawText(int(x + w - 75), int(y + 14), sync_label)

        # 2. Character Viewport
        char_x = x + 6
        char_y = y + 18
        char_w = w - 12
        char_h = h - 90

        # Pedestal rings at her base (A.T. Field octagon for EVA!)
        ped_cx = char_x + char_w / 2.0
        ped_cy = char_y + char_h - 4

        if is_eva:
            # Concentric A.T. Field pulse
            EvaTheme.draw_at_field(painter, QPointF(ped_cx, ped_cy), 28, layers=2, pulse_offset=self.anim_tick * 0.1)
        else:
            ring_color = QColor(CyberTheme.CYAN_CORE)
            ring_color.setAlpha(pulse_alpha)
            painter.setPen(QPen(ring_color, 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(ped_cx, ped_cy), 46, 7)

            inner_ring_color = QColor(CyberTheme.CYAN_BRIGHT)
            inner_ring_color.setAlpha(int(pulse_alpha * 0.8))
            painter.setPen(QPen(inner_ring_color, 1.0))
            painter.drawEllipse(QPointF(ped_cx, ped_cy), 28, 4.5)

        # Upward light cone
        cone_path = QPainterPath()
        cone_path.moveTo(ped_cx - 44, ped_cy)
        cone_path.lineTo(ped_cx + 44, ped_cy)
        cone_path.lineTo(char_x + char_w, char_y)
        cone_path.lineTo(char_x, char_y)
        cone_path.closeSubpath()
        cone_grad = QLinearGradient(ped_cx, ped_cy, ped_cx, char_y)
        cone_color = QColor(255, 102, 0, 30) if is_eva else QColor(0, 240, 255, 35)
        cone_grad.setColorAt(0.0, cone_color)
        cone_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(cone_grad))
        painter.drawPath(cone_path)

        # Character clipping shape
        char_rect = QRectF(char_x, char_y, char_w, char_h - 6)
        clip_path = QPainterPath()
        clip_path.addRoundedRect(char_rect, 4, 4)

        painter.save()
        painter.setClipPath(clip_path)

        # Continuous Animations: Floating / Breathing Bobbing + Gentle Sway
        bob_y = math.sin(self.anim_tick * 0.08) * 3.0
        sway_x = math.cos(self.anim_tick * 0.04) * 1.2

        if self.rq_pixmap and not self.rq_pixmap.isNull():
            scaled_pix = self.rq_pixmap.scaled(
                int(char_w), int(char_h - 6),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(int(char_x + sway_x), int(char_y + bob_y), scaled_pix)
        else:
            painter.fillRect(char_rect, QColor(14, 22, 34))
            painter.setFont(EvaTheme.get_font(8, bold=True))
            painter.setPen(EvaTheme.NERV_ORANGE)
            painter.drawText(char_rect, Qt.AlignCenter, "AYANAMI REI\nONLINE")

        # Subtle TV hologram scanlines
        scan_pen_color = QColor(255, 102, 0, 16) if is_eva else QColor(0, 240, 255, 18)
        painter.setPen(QPen(scan_pen_color, 1))
        for ly in range(int(char_y), int(char_y + char_h), 3):
            painter.drawLine(int(char_x), ly, int(char_x + char_w), ly)

        # Hologram sweeping laser beam line
        scan_y = char_y + (self.anim_tick * 2.2) % (char_h - 8)
        beam_color = EvaTheme.NERV_AMBER if is_eva else CyberTheme.CYAN_BRIGHT
        painter.setPen(QPen(beam_color, 1.8))
        painter.drawLine(int(char_x), int(scan_y), int(char_x + char_w), int(scan_y))

        painter.restore()

        # Viewport border
        painter.setPen(QPen(EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_DIM, 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(char_rect, 4, 4)

        # 3. Interactive Reactive Dialogue Bubble below character
        diag_x = char_x
        diag_y = char_y + char_h + 4
        diag_w = char_w
        diag_h = h - (diag_y - y) - 6

        bubble_rect = QRectF(diag_x, diag_y, diag_w, diag_h)
        painter.setPen(QPen(EvaTheme.NERV_ORANGE if is_eva else CyberTheme.GRID_LINE_BRIGHT, 1.0))
        painter.setBrush(QBrush(QColor(12, 14, 20, 235)))
        painter.drawRoundedRect(bubble_rect, 4, 4)

        # Animated audio equalizer bars bouncing to simulate Eva voice communication
        eq_x = int(diag_x + diag_w - 28)
        eq_heights = [
            int(4 + 5 * math.sin(self.anim_tick * 0.22 + 0.5)),
            int(6 + 6 * math.sin(self.anim_tick * 0.28 + 1.2)),
            int(3 + 4 * math.sin(self.anim_tick * 0.18 + 2.1)),
            int(5 + 5 * math.sin(self.anim_tick * 0.25 + 3.0)),
        ]
        eq_color = EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_BRIGHT
        for bi, bh in enumerate(eq_heights):
            h_clamped = max(2, min(12, bh))
            painter.fillRect(eq_x + bi * 3, int(diag_y + 14 - h_clamped), 2, h_clamped, eq_color)

        # Determine Reactive Speech Text based on Telemetry State
        is_regen = self.telemetry.drive_mode == "REGEN" or self.telemetry.motor_power_kw < -4.0
        high_power = self.telemetry.throttle_pct > 65.0 or self.telemetry.motor_power_kw > 60.0
        g_total = math.sqrt(self.telemetry.g_lat ** 2 + self.telemetry.g_long ** 2)
        high_g = g_total > 0.45
        is_ev = self.telemetry.engine_rpm == 0 and self.telemetry.speed_kmh > 4.0
        high_speed = self.telemetry.speed_kmh > 95.0

        if is_eva:
            # 綾波零 (Rei Ayanami) Iconic Calm Dialogue
            if high_g:
                speech_title = "🌀 G 力急劇上升……"
                speech_desc = "沒問題的，姿勢制御正常。"
                accent_color = EvaTheme.NERV_RED
                sub_tag = f"A.T. FIELD // LAT: {self.telemetry.g_lat:+.2f}G"
            elif is_regen:
                speech_title = "🔋 動能回路啟動"
                speech_desc = "內部電源充填中。"
                accent_color = EvaTheme.ACID_GREEN
                sub_tag = f"REGEN: {int(abs(self.telemetry.motor_power_kw))}kW // CHG"
            elif high_power:
                speech_title = "🔥 A.T.力場全開！"
                speech_desc = "出力限制器解除……衝刺。"
                accent_color = EvaTheme.NERV_RED
                sub_tag = f"POWER: {int(self.telemetry.motor_power_kw)}kW // LIMITER OFF"
            elif high_speed:
                speech_title = "🏎️ 高速巡航態勢"
                speech_desc = "目標距離維持中。"
                accent_color = EvaTheme.NERV_AMBER
                sub_tag = f"SPEED: {int(self.telemetry.speed_kmh)} km/h"
            elif is_ev:
                speech_title = "⚡ 內部電源運作中"
                speech_desc = "神經迴路……無異常。"
                accent_color = EvaTheme.ACID_GREEN
                sub_tag = "INTERNAL POWER // ACTIVE"
            elif self.telemetry.engine_rpm > 1000:
                speech_title = "⚙️ 外部電源直連"
                speech_desc = "發電迴路啟動受諾。"
                accent_color = EvaTheme.NERV_ORANGE
                sub_tag = f"ENG: {self.telemetry.engine_rpm} RPM"
            else:
                speech_title = "這就是……FL4的心跳嗎？"
                speech_desc = "指令受諾，現在出擊。"
                accent_color = EvaTheme.LCL_CYAN
                sub_tag = "SYNCHRO: 94.8% // NOMINAL"
        else:
            # Cyberpunk Dialogue
            if high_g:
                speech_title = "🌀 好強的過彎 G 力！"
                speech_desc = "底盤極限發揮中♪"
                accent_color = CyberTheme.ELECTRIC_BLUE
                sub_tag = f"LAT: {self.telemetry.g_lat:+.2f}G // APEX"
            elif is_regen:
                speech_title = "🔋 動能回收中！"
                speech_desc = "大電池充能回血 UP ↑"
                accent_color = CyberTheme.NEON_GREEN
                sub_tag = f"REGEN: {int(abs(self.telemetry.motor_power_kw))}kW // CHG"
            elif high_power:
                speech_title = "🔥 全電門衝刺！"
                speech_desc = "MG2 雙馬達全力輸出！"
                accent_color = CyberTheme.NEON_RED
                sub_tag = f"POWER: {int(self.telemetry.motor_power_kw)}kW // BOOST"
            elif high_speed:
                speech_title = "🏎️ 高速巡航中"
                speech_desc = "保持安全車距安心開～"
                accent_color = CyberTheme.CYAN_BRIGHT
                sub_tag = f"SPEED: {int(self.telemetry.speed_kmh)} km/h"
            elif is_ev:
                speech_title = "⚡ 純電巡航中～"
                speech_desc = "安靜平順、零油耗♪"
                accent_color = CyberTheme.NEON_GREEN
                sub_tag = "EV MODE // ACTIVE"
            elif self.telemetry.engine_rpm > 1000:
                speech_title = "⚙️ 引擎串聯發電"
                speech_desc = "高效阿金森循環運轉"
                accent_color = CyberTheme.AMBER_CORE
                sub_tag = f"ENG: {self.telemetry.engine_rpm} RPM"
            else:
                speech_title = "Civic e:HEV 狀況絕佳"
                speech_desc = "今天也要開心出發喔♪"
                accent_color = CyberTheme.CYAN_BRIGHT
                sub_tag = "SYSTEM: ALL NOMINAL"

        # Blinking cursor simulation
        cursor = "▌" if (self.anim_tick // 18) % 2 == 0 else ""

        # Draw Speech Title & Description
        painter.setFont(EvaTheme.get_font(8, bold=True) if is_eva else CyberTheme.get_font(8, bold=True))
        painter.setPen(EvaTheme.TEXT_WHITE if is_eva else CyberTheme.TEXT_WHITE)
        painter.drawText(int(diag_x + 6), int(diag_y + 14), speech_title)

        painter.setFont(EvaTheme.get_font(7, bold=False) if is_eva else CyberTheme.get_font(7, bold=False))
        painter.setPen(accent_color)
        painter.drawText(int(diag_x + 6), int(diag_y + 28), speech_desc + cursor)

        # Mini Status Tag Pill at bottom of dialogue bubble
        tag_rect = QRectF(diag_x + 4, diag_y + 36, diag_w - 8, 16)
        if is_eva:
            hazard_stripe_c = EvaTheme.NERV_RED if (high_power or high_g) else EvaTheme.NERV_ORANGE
            EvaTheme.draw_hazard_badge(painter, tag_rect, sub_tag, stripe_color=hazard_stripe_c, text_color=accent_color, font_size=6)
        else:
            tag_border = CyberTheme.CYAN_DIM
            painter.setPen(QPen(tag_border, 0.8))
            painter.setBrush(QBrush(QColor(16, 20, 28, 220)))
            painter.drawRoundedRect(tag_rect, 2, 2)

            painter.setFont(CyberTheme.get_font(6, bold=True, mono=True))
            painter.setPen(accent_color)
            painter.drawText(tag_rect, Qt.AlignCenter, sub_tag)

    def draw_oscilloscope_chart(self, painter, x, y, w, h, data, line_color, min_val, max_val):
        """Draws oscilloscope with gradient-filled area and sweep beam."""
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

        # Glowing waveform stroke
        painter.setPen(QPen(line_color, 1.8))
        painter.drawPath(path)

    def draw_energy_flow_diagram(self, painter, x, y, w, h):
        """Draws schematic nodes and flowing energy particles."""
        is_eva = self.theme == "eva"
        batt_pt = QPointF(x + 36, y + 40)
        motor_pt = QPointF(x + w * 0.48, y + 40)
        eng_pt = QPointF(x + w - 36, y + 40)

        is_regen = self.telemetry.drive_mode == "REGEN" or self.telemetry.motor_power_kw < -2.0
        if is_eva:
            particle_color = EvaTheme.ACID_GREEN if is_regen else EvaTheme.NERV_ORANGE
        else:
            particle_color = CyberTheme.NEON_GREEN if is_regen else CyberTheme.CYAN_CORE

        # Neon conduit lines
        line_color = EvaTheme.GRID_LINE_BRIGHT if is_eva else CyberTheme.GRID_LINE_BRIGHT
        pen_line = QPen(line_color, 3, Qt.DashLine)
        painter.setPen(pen_line)
        painter.drawLine(batt_pt, motor_pt)
        painter.drawLine(motor_pt, eng_pt)

        # Draw Conduit Chevrons >>>
        painter.setFont(EvaTheme.get_font(9, bold=True, mono=True) if is_eva else CyberTheme.get_font(9, bold=True, mono=True))
        if is_eva:
            arrow_color = EvaTheme.NERV_AMBER if not is_regen else EvaTheme.ACID_GREEN
        else:
            arrow_color = CyberTheme.AMBER_CORE if not is_regen else CyberTheme.NEON_GREEN
        painter.setPen(arrow_color)
        mid_bm = QPointF((batt_pt.x() + motor_pt.x()) / 2 - 8, y + 33)
        mid_me = QPointF((motor_pt.x() + eng_pt.x()) / 2 - 8, y + 33)
        flow_arrow = "<<<" if is_regen else ">>>"
        painter.drawText(int(mid_bm.x()), int(mid_bm.y()), flow_arrow)
        painter.drawText(int(mid_me.x()), int(mid_me.y()), flow_arrow)

        # Draw Flowing Particles
        painter.setPen(Qt.NoPen)
        for p in self.particles:
            if p.segment == 0:
                px = batt_pt.x() + (motor_pt.x() - batt_pt.x()) * p.progress
                py = batt_pt.y()
            else:
                px = motor_pt.x() + (eng_pt.x() - motor_pt.x()) * p.progress
                py = motor_pt.y()

            grad = QRadialGradient(px, py, p.size * 2.2)
            c = QColor(particle_color)
            c.setAlpha(220)
            bright_c = EvaTheme.TEXT_WHITE if is_eva else CyberTheme.CYAN_BRIGHT
            grad.setColorAt(0.0, bright_c)
            grad.setColorAt(0.5, c)
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(grad))
            painter.drawEllipse(QPointF(px, py), p.size, p.size)

        # Draw Node Icons
        self.draw_battery_icon(painter, batt_pt)
        self.draw_motor_icon(painter, motor_pt)
        self.draw_engine_icon(painter, eng_pt)

    def draw_battery_icon(self, painter, center: QPointF):
        is_eva = self.theme == "eva"
        box = QRectF(center.x() - 17, center.y() - 13, 34, 26)
        border_c = EvaTheme.NERV_ORANGE if is_eva else CyberTheme.CYAN_CORE
        bg_c = EvaTheme.BG_CARD if is_eva else CyberTheme.BG_CARD
        painter.setPen(QPen(border_c, 2))
        painter.setBrush(QBrush(bg_c))
        painter.drawRoundedRect(box, 4, 4)

        # Bolt / Power icon
        path = QPainterPath()
        cx, cy = center.x(), center.y()
        path.moveTo(cx + 2, cy - 8)
        path.lineTo(cx - 4, cy)
        path.lineTo(cx + 1, cy)
        path.lineTo(cx - 2, cy + 8)
        path.lineTo(cx + 4, cy)
        path.lineTo(cx - 1, cy)
        path.closeSubpath()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(border_c))
        painter.drawPath(path)

    def draw_motor_icon(self, painter, center: QPointF):
        is_eva = self.theme == "eva"
        cx, cy = center.x(), center.y()
        box = QRectF(cx - 16, cy - 16, 32, 32)
        border_c = EvaTheme.ACID_GREEN if is_eva else CyberTheme.CYAN_CORE
        bg_c = EvaTheme.BG_CARD if is_eva else CyberTheme.BG_CARD
        painter.setPen(QPen(border_c, 2))
        painter.setBrush(QBrush(bg_c))
        painter.drawEllipse(box)

        # Ridges
        dim_c = EvaTheme.NERV_AMBER if is_eva else CyberTheme.CYAN_DIM
        painter.setPen(QPen(dim_c, 1.5))
        for angle in (0, 45, 90, 135):
            rad = math.radians(angle)
            dx = 12 * math.cos(rad)
            dy = 12 * math.sin(rad)
            painter.drawLine(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))

    def draw_engine_icon(self, painter, center: QPointF):
        is_eva = self.theme == "eva"
        cx, cy = center.x(), center.y()
        box = QRectF(cx - 17, cy - 13, 34, 26)
        active = self.telemetry.engine_rpm > 400
        if is_eva:
            color = EvaTheme.NERV_RED if active else EvaTheme.TEXT_MUTED
            bg_c = EvaTheme.BG_CARD
        else:
            color = CyberTheme.AMBER_CORE if active else CyberTheme.TEXT_MUTED
            bg_c = CyberTheme.BG_CARD
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(bg_c))
        painter.drawRoundedRect(box, 4, 4)

        painter.setFont(EvaTheme.get_font(8, bold=True) if is_eva else CyberTheme.get_font(8, bold=True))
        painter.setPen(color)
        eng_label = "ENG" if not is_eva else "ENG"
        painter.drawText(box, Qt.AlignCenter, eng_label)

    def draw_eva_concept_panel(self, painter, W, H):
        """
        Renders the authentic EVA concept layout:
        1. Top: INTERNAL BATTERY large countdown + horizontal SoC battery bar
        2. Middle: EMERGENCY // G-FORCE LOCK-ON chevron ribbon
        3. Bottom: MONITOR window with 2D Rei Ayanami + SYNCHRONIZATION RATE 98.4% + dual Biometric wave monitors
        """
        soc = max(0.0, min(100.0, self.telemetry.battery_soc_pct))

        # ==========================================
        # 1. TOP BOX: INTERNAL BATTERY & COUNTDOWN
        # ==========================================
        top_h = 124
        top_rect = QRectF(10, 8, W - 20, top_h)

        # Purple frame & dark background
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 2.0))
        painter.setBrush(QBrush(QColor(8, 6, 14, 250)))
        painter.drawRect(top_rect)

        # Header title
        painter.setFont(EvaTheme.get_serif_font(13, bold=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        painter.drawText(22, 30, "INTERNAL BATTERY")

        # Vertical green level bar on left of countdown
        vbar_rect = QRectF(22, 38, 12, 42)
        painter.fillRect(vbar_rect, EvaTheme.EVA_GREEN)

        # Huge Countdown Clock
        painter.setFont(EvaTheme.get_serif_font(34, bold=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        is_ev = self.telemetry.drive_mode == "EV" or self.telemetry.engine_rpm == 0
        rem_sec = int((soc / 100.0) * 300)
        m = rem_sec // 60
        s = rem_sec % 60
        countdown_str = f"00:{m:02d}:{s:02d}" if is_ev else "00:09:45"
        painter.drawText(42, 74, countdown_str)

        # Horizontal Battery Bar
        bar_x = 22
        bar_y = 88
        bar_w = W - 145
        bar_h = 24

        # Outer frame
        painter.setPen(QPen(EvaTheme.EVA_GREEN, 2.0))
        painter.setBrush(QBrush(QColor(6, 12, 8, 230)))
        painter.drawRect(QRectF(bar_x, bar_y, bar_w, bar_h))

        # Battery terminal positive tip on right of bar
        tip_w = 6
        tip_h = 12
        painter.fillRect(QRectF(bar_x + bar_w + 1, bar_y + (bar_h - tip_h) / 2, tip_w, tip_h), EvaTheme.EVA_GREEN)

        # Liquid green fill
        fill_w = max(4.0, (bar_w - 6) * (soc / 100.0))
        painter.fillRect(QRectF(bar_x + 3, bar_y + 3, fill_w, bar_h - 6), EvaTheme.EVA_GREEN)

        # Segment dividers
        painter.setPen(QPen(QColor(4, 10, 6, 180), 1.5))
        for div_i in range(1, 10):
            dx = bar_x + (bar_w / 10.0) * div_i
            painter.drawLine(int(dx), int(bar_y + 3), int(dx), int(bar_y + bar_h - 3))

        # Percentage text
        painter.setFont(EvaTheme.get_serif_font(12, bold=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        painter.drawText(QRectF(bar_x + bar_w + 10, bar_y + 1, 95, bar_h), Qt.AlignVCenter | Qt.AlignLeft, f"{int(soc)}% SoC")

        # ==========================================
        # 2. MIDDLE CHEVRON ARROW RIBBON
        # ==========================================
        mid_y = top_h + 16
        mid_h = 30
        left_w = (W - 20) * 0.40
        arrow_dx = 14

        # Left emergency trapezoid/arrow pointing right
        poly_left = QPolygonF([
            QPointF(10, mid_y),
            QPointF(10 + left_w, mid_y),
            QPointF(10 + left_w + arrow_dx, mid_y + mid_h / 2),
            QPointF(10 + left_w, mid_y + mid_h),
            QPointF(10, mid_y + mid_h)
        ])
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.5))
        painter.setBrush(QBrush(QColor(56, 18, 90)))
        painter.drawPolygon(poly_left)

        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_WHITE)
        painter.drawText(QRectF(14, mid_y, left_w - 4, mid_h), Qt.AlignCenter, "EMERGENCY\n来リウ")

        # Right G-Force Lock-On banner
        poly_right = QPolygonF([
            QPointF(10 + left_w + 4, mid_y),
            QPointF(W - 10, mid_y),
            QPointF(W - 10, mid_y + mid_h),
            QPointF(10 + left_w + 4, mid_y + mid_h),
            QPointF(10 + left_w + arrow_dx + 4, mid_y + mid_h / 2)
        ])
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.5))
        painter.setBrush(QBrush(QColor(36, 12, 60)))
        painter.drawPolygon(poly_right)

        painter.setFont(EvaTheme.get_font(9, bold=True, mono=True))
        painter.setPen(EvaTheme.LCL_CYAN)
        painter.drawText(QRectF(10 + left_w + arrow_dx + 8, mid_y, (W - 10) - (10 + left_w + arrow_dx + 8), mid_h),
                         Qt.AlignCenter, "G-FORCE LOCK-ON")

        # ==========================================
        # 3. BOTTOM WINDOW: MONITOR & REI AYANAMI
        # ==========================================
        mon_y = mid_y + mid_h + 10
        mon_h = H - mon_y - 10
        mon_w = W - 20

        # Outer purple window frame
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 2.0))
        painter.setBrush(QBrush(QColor(8, 6, 14, 250)))
        painter.drawRect(QRectF(10, mon_y, mon_w, mon_h))

        # Top title bar
        title_h = 22
        painter.fillRect(QRectF(11, mon_y + 1, mon_w - 2, title_h), QColor(48, 16, 78))
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_WHITE)
        painter.drawText(18, int(mon_y + 15), "MONITOR")

        # Window controls
        painter.setFont(EvaTheme.get_font(9, bold=True, mono=True))
        painter.drawText(int(W - 42), int(mon_y + 15), "■ ▲")

        # Inside monitor area
        inner_y = mon_y + title_h + 6
        inner_h = mon_h - title_h - 10
        split_x = 10 + mon_w * 0.32

        # Vertical divider line
        painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.5))
        painter.drawLine(int(split_x), int(inner_y), int(split_x), int(inner_y + inner_h))

        # --- LEFT SUB-PANE: 2D REI AYANAMI ---
        # Vertical green level bar on left of portrait
        lvl_w = 7
        lvl_x = 16
        lvl_y = inner_y + 4
        lvl_h = inner_h - 28
        painter.setPen(QPen(EvaTheme.EVA_GREEN, 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(lvl_x, lvl_y, lvl_w, lvl_h))

        # Stepped green segments
        for seg_i in range(12):
            sy = lvl_y + lvl_h - (seg_i + 1) * (lvl_h / 12.0)
            painter.fillRect(QRectF(lvl_x + 1, sy + 1, lvl_w - 2, (lvl_h / 12.0) - 2), EvaTheme.EVA_GREEN)

        painter.setFont(EvaTheme.get_font(6, bold=True, mono=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        painter.drawText(int(lvl_x - 1), int(lvl_y + lvl_h + 12), "50%")

        # Rei Ayanami 2D Portrait with smooth breathing respiration & posture dynamics
        char_x = lvl_x + lvl_w + 6
        char_w = split_x - char_x - 6
        char_h = inner_h - 14

        char_rect = QRectF(char_x, inner_y, char_w, char_h)

        # Smooth sine-wave respiration & posture sway
        t = self.anim_tick * 0.07
        bob_y = math.sin(t) * 4.5
        breath_scale_x = 1.0 + 0.018 * math.sin(t)
        breath_scale_y = 1.0 + 0.032 * math.sin(t)
        tilt_deg = math.sin(t * 0.5) * 1.5 - (self.telemetry.g_lat / 1.5) * 3.5

        if self.rq_pixmap and not self.rq_pixmap.isNull():
            painter.save()
            clip_p = QPainterPath()
            clip_p.addRoundedRect(char_rect, 4, 4)
            painter.setClipPath(clip_p)

            # Deep Entry Plug cockpit background fill
            painter.fillRect(char_rect, QColor(4, 6, 12, 255))

            # Ascending L.C.L. micro-bubbles
            for bi in range(6):
                bp_y = (inner_y + char_h) - ((self.anim_tick * 1.8 + bi * 38) % char_h)
                bp_x = char_x + 6 + (bi * 19) % int(max(10, char_w - 12))
                b_alpha = int(110 + 80 * math.sin(t * 1.5 + bi))
                painter.fillRect(QRectF(bp_x, bp_y, 2.5, 2.5), QColor(0, 240, 255, b_alpha))

            # Scaled pixmap with margin for dynamic transform
            margin_w = int(char_w * 1.12)
            margin_h = int(char_h * 1.12)
            scaled_pix = self.rq_pixmap.scaled(
                margin_w, margin_h,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            # Anchor transform at bottom center of character
            pivot_x = char_x + char_w / 2.0
            pivot_y = inner_y + char_h

            painter.translate(pivot_x, pivot_y)
            painter.rotate(tilt_deg)
            painter.scale(breath_scale_x, breath_scale_y)
            painter.translate(-pivot_x, -pivot_y + bob_y)

            draw_x = char_x - (margin_w - char_w) / 2.0
            draw_y = inner_y - (margin_h - char_h) / 2.0
            painter.drawPixmap(int(draw_x), int(draw_y), scaled_pix)
            painter.restore()

            # Hologram sweeping laser beam line with glow
            scan_y = inner_y + (self.anim_tick * 2.5) % (char_h - 4)
            painter.save()
            painter.setClipPath(clip_p)
            painter.setPen(QPen(QColor(0, 255, 64, 180), 2.0))
            painter.drawLine(int(char_x), int(scan_y), int(char_x + char_w), int(scan_y))
            # Scanline glow trail
            trail_grad = QLinearGradient(char_x, scan_y - 12, char_x, scan_y)
            trail_grad.setColorAt(0.0, QColor(0, 255, 64, 0))
            trail_grad.setColorAt(1.0, QColor(0, 255, 64, 45))
            painter.fillRect(QRectF(char_x, scan_y - 12, char_w, 12), QBrush(trail_grad))
            painter.restore()

            # Viewport border
            painter.setPen(QPen(EvaTheme.EVA_PURPLE_FRAME, 1.2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(char_rect, 4, 4)

            # Tactical HUD tag in portrait: [ ● LIVE LINK ]
            hud_rect = QRectF(char_x + 4, inner_y + 4, 66, 14)
            painter.fillRect(hud_rect, QColor(0, 0, 0, 160))
            live_dot_color = EvaTheme.EVA_GREEN if (self.anim_tick % 30 < 20) else QColor(40, 80, 40)
            painter.fillRect(QRectF(char_x + 8, inner_y + 8, 5, 5), live_dot_color)
            painter.setFont(EvaTheme.get_font(6, bold=True, mono=True))
            painter.setPen(EvaTheme.EVA_GREEN)
            painter.drawText(QRectF(char_x + 16, inner_y + 4, 52, 14), Qt.AlignVCenter | Qt.AlignLeft, "LIVE LINK")

        # --- RIGHT SUB-PANE: SYNCHRONIZATION RATE & DUAL BIOMETRIC OSCILLOSCOPES ---
        right_x = split_x + 8
        right_w = (10 + mon_w) - right_x - 8

        # Title: SYNCHRONIZATION RATE
        painter.setFont(EvaTheme.get_serif_font(8.5, bold=True))
        painter.setPen(EvaTheme.TEXT_WHITE)
        painter.drawText(int(right_x), int(inner_y + 14), "SYNCHRONIZATION RATE")

        # Giant Sync percentage: 98.4%
        sync_val = 98.4 + 0.4 * math.sin(self.anim_tick * 0.05)
        painter.setFont(EvaTheme.get_serif_font(30, bold=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        painter.drawText(int(right_x), int(inner_y + 48), f"{sync_val:.1f}%")

        # Dual Waveform Oscilloscopes
        wave_h = (inner_h - 124) / 2.0
        w1_y = inner_y + 54

        # Wave 1: BIOMETRIC TELEMETRY (Voltage)
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_WHITE)
        painter.drawText(int(right_x), int(w1_y + 10), "BIOMETRIC TELEMETRY")
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        painter.drawText(int(right_x + right_w - 46), int(w1_y + 10), f"{self.telemetry.battery_voltage_v:.0f}V")

        self.draw_concept_wave(painter, right_x, w1_y + 14, right_w, wave_h,
                               self.telemetry.voltage_history, EvaTheme.EVA_GREEN, 160.0, 190.0)

        # Wave 2: BIOMETRIC (Temperature)
        w2_y = w1_y + wave_h + 18
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.TEXT_WHITE)
        painter.drawText(int(right_x), int(w2_y + 10), "BIOMETRIC")
        painter.setFont(EvaTheme.get_font(8, bold=True, mono=True))
        painter.setPen(EvaTheme.EVA_GREEN)
        painter.drawText(int(right_x + right_w - 46), int(w2_y + 10), f"{self.telemetry.battery_temp_c}°C")

        self.draw_concept_wave(painter, right_x, w2_y + 14, right_w, wave_h,
                               self.telemetry.batt_temp_history, EvaTheme.EVA_GREEN, 15.0, 45.0)

        # ==========================================
        # 4. REI AYANAMI DEDICATED REACTIVE DIALOGUE & EQUALIZER
        # ==========================================
        diag_y = w2_y + wave_h + 8
        diag_h = inner_y + inner_h - diag_y - 3
        diag_rect = QRectF(right_x, diag_y, right_w, diag_h)

        # Determine Telemetry State
        g_total = math.sqrt(self.telemetry.g_lat ** 2 + self.telemetry.g_long ** 2)
        is_high_power = (self.telemetry.throttle_pct > 60.0 or self.telemetry.motor_power_kw > 40.0)
        is_regen = (self.telemetry.drive_mode == "REGEN" or self.telemetry.motor_power_kw < -3.0)
        is_high_g = (g_total > 0.40)
        is_engine_gen = (self.telemetry.engine_rpm > 100 or self.telemetry.drive_mode in ("HYBRID", "ENGINE"))
        is_ev_cruise = (self.telemetry.drive_mode == "EV" or (self.telemetry.engine_rpm == 0 and self.telemetry.speed_kmh > 0))

        if is_high_power:
            speech_tag = "🔥 大腳油門 / 高功率"
            speech_text = "「A.T.力場全開！出力限制器解除……衝刺。」"
            accent_color = EvaTheme.NERV_RED
        elif is_high_g:
            speech_tag = "🌀 過彎 G 力飆高"
            speech_text = "「G 力急劇上升……沒問題的，姿勢制御正常。」"
            accent_color = EvaTheme.NERV_ORANGE
        elif is_regen:
            speech_tag = "🔋 動能回收 (Regen)"
            speech_text = "「動能回路啟動，內部電源充填中。」"
            accent_color = EvaTheme.EVA_GREEN
        elif is_engine_gen:
            speech_tag = "⚙️ 外部發電 (Hybrid)"
            speech_text = "「外部電源直連，發電迴路啟動受諾。」"
            accent_color = EvaTheme.NERV_AMBER
        else:
            speech_tag = "⚡ 純電巡航 (EV)"
            speech_text = "「內部電源運作中，神經迴路……無異常。」"
            accent_color = EvaTheme.EVA_GREEN

        painter.setPen(QPen(accent_color, 1.2))
        painter.setBrush(QBrush(QColor(10, 8, 16, 250)))
        painter.drawRoundedRect(diag_rect, 3, 3)

        # Line 1: Speech Status Tag (Left) & Animated 6-Band Jumping Audio Equalizer (Right)
        painter.setFont(EvaTheme.get_font(7, bold=True))
        painter.setPen(accent_color)
        painter.drawText(QRectF(right_x + 6, diag_y + 3, right_w - 60, 14), Qt.AlignVCenter | Qt.AlignLeft, speech_tag)

        # Jumping Audio Equalizer
        eq_w = 44
        eq_x = right_x + right_w - eq_w - 6
        eq_y = diag_y + 3
        for bi in range(6):
            bh = int(3 + 8 * abs(math.sin(self.anim_tick * 0.28 + bi * 0.9)))
            painter.fillRect(QRectF(eq_x + bi * 7, eq_y + 11 - bh, 4, bh), accent_color)

        # Line 2: Full Rei Ayanami Dialogue Quote
        painter.setFont(EvaTheme.get_font(7, bold=True))
        painter.setPen(EvaTheme.TEXT_WHITE)
        painter.drawText(QRectF(right_x + 4, diag_y + 17, right_w - 8, 18), Qt.AlignVCenter | Qt.AlignLeft, speech_text)

    def draw_concept_wave(self, painter, x, y, w, h, data, color, min_val, max_val):
        """Draws neon green biometric oscilloscope waveform on pure black background."""
        box = QRectF(x, y, w, h)
        painter.fillRect(box, QColor(0, 0, 0, 255))
        painter.setPen(QPen(QColor(30, 45, 30), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(box)

        # Subtle grid
        painter.setPen(QPen(QColor(15, 30, 15), 1.0, Qt.DotLine))
        painter.drawLine(int(x), int(y + h / 2), int(x + w), int(y + h / 2))
        painter.drawLine(int(x + w / 2), int(y), int(x + w / 2), int(y + h))

        if not data or len(data) < 2:
            return

        path = QPainterPath()
        span = max(1.0, max_val - min_val)
        step_x = w / (len(data) - 1)

        for idx, val in enumerate(data):
            norm = (val - min_val) / span
            norm = max(0.0, min(1.0, norm))
            px = x + idx * step_x
            py = y + h - (norm * (h - 4)) - 2
            if idx == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)

        painter.setPen(QPen(color, 1.5))
        painter.drawPath(path)
