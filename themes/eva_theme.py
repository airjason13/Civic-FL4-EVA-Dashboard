"""
EVA Theme: Neon Genesis Evangelion / NERV / Rei Ayanami Aesthetic
Features:
- NERV Command Center Dark Palette (Black, EVA Orange, Acid Green, Crimson Red, Eva Purple)
- Octagonal A.T. FIELD geometric shapes
- Emergency hazard diagonal stripes
- High-contrast technical typography
"""

import math
from PyQt5.QtGui import QColor, QFont, QPen, QBrush, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF


class EvaTheme:
    # Backgrounds
    BG_DARK = QColor("#020204")
    BG_CARD = QColor("#07050c")
    BG_CARD_BORDER = QColor("#221a2e")

    # EVA Concept Palette (Authentic Concept Layout)
    EVA_GREEN = QColor("#00ff40")           # Lime Acid Green (Battery Countdown & Sync Rate)
    EVA_YELLOW = QColor("#fff8b0")          # Cream Amber / Gold (Serif Speed Display)
    EVA_PURPLE_FRAME = QColor("#542084")    # Deep NERV Purple Frame
    EVA_RED_BANNER = QColor("#d00818")      # Emergency Warning Red Ribbon
    HEX_AMBER = QColor("#d07810")           # MAGI Honeycomb Amber
    HEX_PURPLE = QColor("#5a2488")          # MAGI Honeycomb Purple
    HEX_BG = QColor("#0c0a14")              # Honeycomb Cell Dark Fill

    # EVA Unit-00 & NERV Palette
    NERV_ORANGE = QColor("#ff6600")         # Primary NERV Alert Orange
    NERV_AMBER = QColor("#ffaa00")          # Warning Amber
    NERV_RED = QColor("#ff1a2a")            # Emergency Crimson
    ACID_GREEN = QColor("#00ff40")          # Internal Battery / Nominal Sync
    EVA_PURPLE = QColor("#4c1c80")          # Test Type-01 Deep Purple
    EVA_PURPLE_BRIGHT = QColor("#8a38d9")
    LCL_CYAN = QColor("#00e5ff")            # L.C.L. / Cockpit HUD Cyan
    LCL_PALE = QColor("#d0f8ff")            # Rei plugsuit pale highlight
    
    # Grayscale / Technical
    TEXT_WHITE = QColor("#ffffff")
    TEXT_MUTED = QColor("#7a7288")
    TEXT_DIM = QColor("#3c3648")
    GRID_LINE = QColor("#14101e")
    GRID_LINE_BRIGHT = QColor("#2a2038")

    @staticmethod
    def get_font(size=12, bold=False, mono=False):
        """Returns sharp, high-contrast technical anime font."""
        family = "Monospace" if mono else "DejaVu Sans"
        font = QFont(family, int(round(size)))
        font.setBold(bold)
        font.setStyleStrategy(QFont.PreferAntialias)
        return font

    @staticmethod
    def get_serif_font(size=12, bold=False):
        """Returns classic Evangelion NERV serif typography."""
        font = QFont("DejaVu Serif", int(round(size)))
        font.setBold(bold)
        font.setStyleStrategy(QFont.PreferAntialias)
        return font

    @staticmethod
    def draw_pointy_hexagon(painter, cx: float, cy: float, r: float, border_color: QColor, fill_color: QColor = None, line_width: float = 1.5):
        """Draws pointy-topped regular hexagon for MAGI honeycomb matrix."""
        poly = QPolygonF()
        for i in range(6):
            rad = math.radians(30 + i * 60.0)
            poly.append(QPointF(cx + r * math.cos(rad), cy + r * math.sin(rad)))

        painter.save()
        painter.setRenderHint(painter.Antialiasing, True)
        painter.setPen(QPen(border_color, line_width))
        if fill_color:
            painter.setBrush(QBrush(fill_color))
        else:
            painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(poly)
        painter.restore()

    @staticmethod
    def draw_nerv_frame(painter, rect: QRectF, border_color: QColor = None, corner_cut: float = 8.0, fill_color: QColor = None):
        """Draws NERV chamfered tactical frame with hazard bracket corners."""
        if border_color is None:
            border_color = EvaTheme.NERV_ORANGE
        if fill_color is None:
            fill_color = EvaTheme.BG_CARD

        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        c = corner_cut

        path = QPainterPath()
        path.moveTo(x + c, y)
        path.lineTo(x + w - c, y)
        path.lineTo(x + w, y + c)
        path.lineTo(x + w, y + h - c)
        path.lineTo(x + w - c, y + h)
        path.lineTo(x + c, y + h)
        path.lineTo(x, y + h - c)
        path.lineTo(x, y + c)
        path.closeSubpath()

        painter.save()
        painter.setRenderHint(painter.Antialiasing, True)
        painter.setPen(QPen(border_color, 1.2))
        painter.setBrush(QBrush(fill_color))
        painter.drawPath(path)

        # Draw Corner Hazard Brackets
        pen_bracket = QPen(EvaTheme.NERV_ORANGE, 2.0)
        painter.setPen(pen_bracket)
        b_len = 10.0

        # Top-Left Bracket
        painter.drawLine(int(x), int(y + c + b_len), int(x), int(y + c))
        painter.drawLine(int(x), int(y + c), int(x + c), int(y))
        painter.drawLine(int(x + c), int(y), int(x + c + b_len), int(y))

        # Bottom-Right Bracket
        painter.drawLine(int(x + w), int(y + h - c - b_len), int(x + w), int(y + h - c))
        painter.drawLine(int(x + w), int(y + h - c), int(x + w - c), int(y + h))
        painter.drawLine(int(x + w - c), int(y + h), int(x + w - c - b_len), int(y + h))

        painter.restore()

    @staticmethod
    def draw_hazard_stripes(painter, rect: QRectF, stripe_color=None, bg_color=None, stripe_width=6, step=12, border=True):
        """Draws iconic bold NERV emergency orange/black or amber/black hazard diagonal stripes."""
        if stripe_color is None:
            stripe_color = EvaTheme.NERV_ORANGE
        if bg_color is None:
            bg_color = QColor(10, 10, 15, 240)

        painter.save()
        painter.setClipRect(rect)
        painter.fillRect(rect, bg_color)

        pen = QPen(stripe_color, stripe_width)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)

        # 45-degree bold diagonal parallel stripes
        h = rect.height()
        w = rect.width()
        x0 = int(rect.x() - h - 10)
        x1 = int(rect.x() + w + h + 10)
        y0 = int(rect.y())
        y1 = int(rect.y() + h)

        for ix in range(x0, x1, step):
            painter.drawLine(ix, y1, ix + int(h * 1.05), y0)

        if border:
            painter.setPen(QPen(stripe_color, 1.0))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect)

        painter.restore()

    @staticmethod
    def draw_hazard_badge(painter, rect: QRectF, text: str, text_color=None, stripe_color=None, bg_color=None, font_size=8):
        """
        Draws iconic Evangelion hazard stripe banner with solid center text plate:
        [ /// ///// ]  TEXT TITLE  [ ///// /// ]
        """
        if stripe_color is None:
            stripe_color = EvaTheme.NERV_ORANGE
        if bg_color is None:
            bg_color = QColor(10, 10, 15, 240)
        if text_color is None:
            text_color = EvaTheme.NERV_ORANGE

        painter.save()
        # Draw background hazard stripes across entire banner
        EvaTheme.draw_hazard_stripes(painter, rect, stripe_color=stripe_color, bg_color=bg_color, stripe_width=5, step=10, border=True)

        # Center black plate for text
        painter.setFont(EvaTheme.get_font(font_size, bold=True, mono=True))
        text_w = painter.fontMetrics().horizontalAdvance(text) + 16
        center_x = rect.x() + (rect.width() - text_w) / 2.0
        plate_rect = QRectF(center_x, rect.y(), text_w, rect.height())

        painter.setPen(QPen(stripe_color, 1.2))
        painter.setBrush(QBrush(QColor(8, 10, 16, 250)))
        painter.drawRect(plate_rect)

        painter.setPen(text_color)
        painter.drawText(plate_rect, Qt.AlignCenter, text)
        painter.restore()

    @staticmethod
    def draw_at_field(painter, center: QPointF, radius: float, layers=3, pulse_offset=0.0):
        """
        Draws the iconic concentric octagonal A.T. FIELD (Absolute Terror Field)
        with golden/orange glowing barrier lines.
        """
        painter.save()
        painter.setRenderHint(painter.Antialiasing, True)

        cx, cy = center.x(), center.y()
        for layer in range(layers):
            r = radius * ((layer + 1) / float(layers))
            # Octagon points (8 vertices at 22.5, 67.5, 112.5... degrees)
            poly = QPolygonF()
            for i in range(8):
                angle_deg = 22.5 + i * 45.0
                rad = math.radians(angle_deg)
                poly.append(QPointF(cx + r * math.cos(rad), cy + r * math.sin(rad)))

            alpha = int(120 + 80 * math.sin(pulse_offset + layer * 1.2))
            c = QColor(EvaTheme.NERV_ORANGE)
            c.setAlpha(max(50, min(255, alpha)))

            painter.setPen(QPen(c, 1.8 if layer == layers - 1 else 1.0))
            painter.setBrush(Qt.NoBrush)
            painter.drawPolygon(poly)

        painter.restore()
