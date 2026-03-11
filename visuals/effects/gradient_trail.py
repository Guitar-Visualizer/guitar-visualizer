from PySide6.QtGui import QPainter, QColor, QBrush, QLinearGradient
from PySide6.QtCore import QRectF, Qt
from visuals.effects.base_effect import Effect, get_canvas_height


class GradientTrail(Effect):

    def __init__(self, x: float, y: float, end_y: float, start_color: QColor, end_color: QColor):
        super().__init__(x, y, start_color)
        self.start_color = start_color
        self.end_color = end_color
        self.start_y = y
        self.end_y = end_y
        self.width = get_canvas_height() * 0.15
        self.lifetime = float('inf')

    def render(self, painter: QPainter):
        if self.start_y == self.end_y:
            return
        gradient = QLinearGradient(self.x, self.start_y, self.x, self.end_y)
        gradient.setColorAt(0.0, self.start_color)
        gradient.setColorAt(1.0, self.end_color)
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(
            QRectF(self.x - self.width / 2, self.start_y, self.width, self.end_y - self.start_y),
            self.width / 2, self.width / 2)
