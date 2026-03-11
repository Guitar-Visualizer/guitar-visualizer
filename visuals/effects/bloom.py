"""
Watercolor bloom effect
"""

from PySide6.QtGui import QPainter, QColor, QBrush, QRadialGradient
from PySide6.QtCore import QRectF, Qt
from visuals.effects.base_effect import Effect

from visuals.effects.base_effect import CANVAS_WIDTH, CANVAS_HEIGHT


class WatercolorBloom(Effect):
  
    
    def __init__(self, x: float, y: float, color: QColor):
        super().__init__(x, y, color)
       
        self.max_radius = CANVAS_HEIGHT * 0.15
        self.is_sustained = True
        self.lifetime = float('inf')
        self.radius = 0.0
    
    def release(self):
        self.is_sustained = False
    
    def update(self, dt: float):
        super().update(dt)
        if self.is_sustained:
            self.radius += self.max_radius*dt
            if self.radius >= self.max_radius:  # stop growing at max
                self.radius = self.max_radius
                self.is_sustained = False
    
    def render(self, painter: QPainter):
        if self.radius <= 0:
            return
   
        gradient = QRadialGradient(self.x, self.y, self.radius)
        center_color = QColor(self.color)
        center_color.setAlpha(180)   # slightly transparent even at center, watercolor feel
        edge_color = QColor(self.color)
        edge_color.setAlpha(0) 
        gradient.setColorAt(0.0, center_color)   # center
        gradient.setColorAt(1.0, edge_color)     # edge
        # TODO: Draw circle with gradient
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)  # no outline
        painter.drawEllipse(QRectF(self.x - self.radius, self.y - self.radius, 
                                   self.radius * 2, self.radius * 2))


    