import random
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QApplication

def _get_dim(attr, fallback):
    app = QApplication.instance()
    if app:
        screen = app.primaryScreen().geometry()
        return getattr(screen, attr)()
    return fallback

def get_canvas_width():
    return _get_dim('width', 800)

def get_canvas_height():
    return _get_dim('height', 600)

# module-level fallbacks, replaced at runtime
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


class Effect:
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
        pass


class EffectManager:
    def __init__(self):
        self.effects = []
        self.current_x = 0
        self.x_step = get_canvas_width() / 100

    def add_effect(self, effect, note_number: int):
        h = get_canvas_height()
        w = get_canvas_width()
        if note_number >= 64:
            y = random.randrange(0, h // 2)
        else:
            y = random.randrange(h // 2, h)
        effect.y = y
        effect.x = self.current_x
        self.current_x += self.x_step
        if self.current_x >= w:
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
