"""
Cyberpunk Theme Constants & QPainter Styling Helpers
Defines color palette, glow strokes, and UI rendering utilities.
"""

from PyQt5.QtGui import QColor, QFont, QPen, QBrush, QLinearGradient, QRadialGradient, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF


class CyberTheme:
    # Backgrounds
    BG_DARK = QColor("#080a0f")
    BG_CARD = QColor("#0e131b")
    BG_CARD_BORDER = QColor("#1c2636")

    # Neon Accents
    CYAN_CORE = QColor("#00f0ff")        # Pure glowing cyan
    CYAN_DIM = QColor("#0088aa")
    CYAN_BRIGHT = QColor("#b3ffff")
    ELECTRIC_BLUE = QColor("#0066ff")
    NEON_GREEN = QColor("#00ff88")       # Charge / Eco / OK
    NEON_PINK = QColor("#ff007f")        # Cyberpunk accent pink
    AMBER_CORE = QColor("#ffaa00")       # Power / Engine / Warning
    AMBER_DIM = QColor("#885500")
    NEON_RED = QColor("#ff2244")         # Danger / Peak

    # Grayscale / Neutral
    TEXT_WHITE = QColor("#ffffff")
    TEXT_MUTED = QColor("#5a6e85")
    TEXT_DIM = QColor("#38485c")
    GRID_LINE = QColor("#121b27")
    GRID_LINE_BRIGHT = QColor("#1c2b3d")

    @staticmethod
    def get_font(size=12, bold=False, mono=False):
        """Returns crisp automotive UI font."""
        family = "Monospace" if mono else "DejaVu Sans"
        font = QFont(family, size)
        font.setBold(bold)
        font.setStyleStrategy(QFont.PreferAntialias)
        return font

    @staticmethod
    def draw_tech_frame(painter: QPainter, rect: QRectF, border_color: QColor = None, corner_cut: float = 10.0, fill_color: QColor = None):
        """
        Draws a futuristic chamfered sci-fi panel with 45-degree cut corners,
        glowing border accents, and tactical corner brackets.
        """
        if border_color is None:
            border_color = CyberTheme.BG_CARD_BORDER
        if fill_color is None:
            fill_color = CyberTheme.BG_CARD

        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        c = corner_cut

        # Chamfered 45-degree polygon path
        from PyQt5.QtGui import QPainterPath
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

        # Fill background
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(border_color, 1.2))
        painter.setBrush(QBrush(fill_color))
        painter.drawPath(path)

        # Draw tech corner highlight brackets
        bracket_len = min(c * 1.5, 14.0)
        pen_bracket = QPen(CyberTheme.CYAN_CORE, 2.0)
        painter.setPen(pen_bracket)

        # Top-Left bracket
        painter.drawLine(int(x), int(y + c + bracket_len), int(x), int(y + c))
        painter.drawLine(int(x), int(y + c), int(x + c), int(y))
        painter.drawLine(int(x + c), int(y), int(x + c + bracket_len), int(y))

        # Bottom-Right bracket
        painter.drawLine(int(x + w), int(y + h - c - bracket_len), int(x + w), int(y + h - c))
        painter.drawLine(int(x + w), int(y + h - c), int(x + w - c), int(y + h))
        painter.drawLine(int(x + w - c), int(y + h), int(x + w - c - bracket_len), int(y + h))

        painter.restore()

    @staticmethod
    def draw_carbon_pattern(painter: QPainter, rect: QRectF):
        """Draws subtle sci-fi carbon-fiber hexagonal micro-grid texture."""
        painter.save()
        painter.setClipRect(rect)
        pen = QPen(QColor(255, 255, 255, 6), 1)
        painter.setPen(pen)

        step = 14
        x0, y0 = int(rect.x()), int(rect.y())
        x1, y1 = int(rect.x() + rect.width()), int(rect.y() + rect.height())

        for ix in range(x0, x1 + step, step):
            painter.drawLine(ix, y0, ix, y1)
        for iy in range(y0, y1 + step, step):
            painter.drawLine(x0, iy, x1, iy)

        # Diagonal accent dots
        dot_pen = QPen(QColor(0, 240, 255, 12), 1.5)
        painter.setPen(dot_pen)
        for ix in range(x0, x1 + step * 2, step * 2):
            for iy in range(y0, y1 + step * 2, step * 2):
                painter.drawPoint(ix, iy)

        painter.restore()

    @staticmethod
    def draw_neon_path(painter: QPainter, path, color: QColor, core_width: float = 2.0, glow_passes: int = 3):
        """Draws glowing neon stroke using multi-pass pen dilation."""
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        widths = [core_width * 4.5, core_width * 2.8, core_width * 1.6]
        alphas = [20, 55, 110]

        for w, a in zip(widths[:glow_passes], alphas[:glow_passes]):
            c = QColor(color)
            c.setAlpha(a)
            pen = QPen(c, w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

        c_core = QColor(color)
        c_core.setAlpha(255)
        pen_core = QPen(c_core, core_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_core)
        painter.drawPath(path)
        painter.restore()

    @staticmethod
    def draw_neon_line(painter: QPainter, p1: QPointF, p2: QPointF, color: QColor, core_width: float = 2.0):
        """Draws a single glowing neon line segment."""
        from PyQt5.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        CyberTheme.draw_neon_path(painter, path, color, core_width)

    @staticmethod
    def draw_hazard_stripes(painter: QPainter, rect: QRectF, color: QColor = None, stripe_width: float = 6.0):
        """Draws cyberpunk 45-degree hazard warning stripes inside the rect."""
        if color is None:
            color = CyberTheme.AMBER_CORE
        painter.save()
        painter.setClipRect(rect)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        pen = QPen(color, stripe_width)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)

        step = stripe_width * 2.2
        start_x = x - h
        end_x = x + w + h

        cur_x = start_x
        while cur_x < end_x:
            painter.drawLine(int(cur_x), int(y + h), int(cur_x + h), int(y))
            cur_x += step

        painter.restore()

    @staticmethod
    def draw_slanted_rect(painter: QPainter, rect: QRectF, slant_dx: float = 8.0, fill_color: QColor = None, border_color: QColor = None):
        """Draws a sporty race-dash slanted parallelogram segment."""
        from PyQt5.QtGui import QPainterPath
        path = QPainterPath()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        path.moveTo(x + slant_dx, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w - slant_dx, y + h)
        path.lineTo(x, y + h)
        path.closeSubpath()

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        if border_color:
            painter.setPen(QPen(border_color, 1.0))
        else:
            painter.setPen(Qt.NoPen)
        if fill_color:
            painter.setBrush(QBrush(fill_color))
        else:
            painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        painter.restore()
