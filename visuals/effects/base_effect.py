"""
Base effect classes
"""

import random
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QApplication

def get_screen_size():
    screen = QApplication.primaryScreen().geometry()
    return screen.width(), screen.height()

CANVAS_WIDTH, CANVAS_HEIGHT = get_screen_size()


class Effect:
    """Base class for visual effects"""

    def __init__(self, x: float, y: float, color: QColor):
        self.x = x
        self.y = y
        self.color = color
        self.age = 0.0
        self.lifetime = 3.0
        self.is_expired = False

    def update(self, dt: float):
        self.age += dt
        if self.age >= self.lifetime:
            self.is_expired = True

    def render(self, painter: QPainter):
        pass  # overridden in subclasses


class EffectManager:
    """Manages all active effects"""

    def __init__(self):
        self.effects = []
        self.current_x = 0
        self.x_step = CANVAS_WIDTH / 100

    def add_effect(self, effect: Effect, note_number: int):
        if note_number >= 60:
            y = random.randrange(0, CANVAS_HEIGHT // 2)
        else:
            y = random.randrange(CANVAS_HEIGHT // 2, CANVAS_HEIGHT)
        effect.y = y
        effect.x = self.current_x
        self.current_x += self.x_step
        if self.current_x >= CANVAS_WIDTH:
            self.current_x = random.randint(0, 50)
        self.effects.append(effect)
        if len(self.effects) >= 60:
            self.effects.pop(0)

    def update(self, dt: float):
        for e in self.effects:
            e.update(dt)
        self.effects = [e for e in self.effects if not e.is_expired]

    def render(self, painter: QPainter):
        for e in self.effects:
            e.render(painter)