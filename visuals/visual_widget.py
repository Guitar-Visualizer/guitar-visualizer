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
        
        
    
    def on_audio_event(self, analysis: dict):
        if not analysis['has_note']:
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
        

       