"""
Visual rendering widget
"""
import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter
from config.color_mapping import ColorMapper
from visuals.effects.base_effect import EffectManager
from visuals.effects.bloom import WatercolorBloom
#from visuals.effects.droplet import WaterDroplet
from visuals.effects.gradient_trail import GradientTrail
class VisualWidget(QWidget):
    """Main visual canvas"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.color_mapper = ColorMapper()
        self.effect_manager = EffectManager()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(33)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        
    
    def on_audio_event(self, analysis: dict):

        if not analysis['has_note']:
            if self.current_bloom is not None:
                self.current_bloom.release()
                self.current_bloom = None
            return
        if analysis['note_number'] is None:
            return
        print(f"event received: {analysis['has_note']}")  # add this
        note_number = analysis['note_number']
        amplitude = analysis['amplitude']
        color = self.color_mapper.note_to_color(note_number, amplitude)
        technique = analysis.get('technique', 'normal')
        print(f"technique: {technique}, note: {note_number}")
        if technique =='normal':
            effect = WatercolorBloom(0, 0, color)
        elif technique == 'hammer_on':
            effect = WatercolorBloom(0,0, color)
        elif technique == 'slide_up' or technique == 'slide_down':
            end_note = note_number
            if end_note >= 60:
                end_y = random.randrange(0, self.height() // 2)
            else:
                end_y = random.randrange(self.height() // 2, self.height())
            effect = GradientTrail(0, 0, end_y, color, color)
            #REPLACE WITH DIFF VIS EFFECTS
        elif technique == 'bend':
            effect =WatercolorBloom(0,0, color)
        elif technique == 'vibrato':
            effect = WatercolorBloom(0,0, color)
        elif technique == 'pull_off':
            effect = WatercolorBloom(0,0, color)
        else:
            effect = WatercolorBloom(0, 0, color)
        self.effect_manager.add_effect(effect, note_number)       
    
    def paintEvent(self, event):
        """Render all effects"""
        painter = QPainter(self)
        dt = 1/30
        painter.fillRect(self.rect(), Qt.black) 
        self.effect_manager.update(dt)
        self.effect_manager.render(painter)
        

    def keyPressEvent(self, event):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QColor
        import random
        print(f"key pressed: {event.key()}")
        key = event.key()
        # generate a random note and color for testing
        note_number = random.randint(50, 80)
        color = self.color_mapper.note_to_color(note_number, 0.8)
        
        if key == Qt.Key.Key_1:
            # normal bloom
            effect = WatercolorBloom(0, 0, color)
            self.current_bloom = effect
            self.effect_manager.add_effect(effect, note_number)
        elif key == Qt.Key.Key_2:
            color = self.color_mapper.note_to_color(note_number, 0.8)
            end_color = self.color_mapper.note_to_color(note_number + 7, 0.8)  # different color at end
            start_y = 100
            end_y = self.height() - 100  # nearly full screen height
            effect = GradientTrail(0, start_y, end_y, color, end_color)
            self.effect_manager.add_effect(effect, note_number)
        elif key == Qt.Key.Key_3:
                    
            self.effect_manager.effects.clear()