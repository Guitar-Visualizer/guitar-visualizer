"""
Main visualizer scene
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from visuals.visual_widget import VisualWidget
from audio.audio_engine import AudioEngine
from PySide6.QtWidgets import QVBoxLayout


class VisualizerScene(QWidget):
    """Recording/playback scene"""
    
    session_ended = Signal()
    
    def __init__(self, project_manager):
        super().__init__()
        self.project_manager = project_manager
        self.visual_widget = VisualWidget()
        self.audio_engine = AudioEngine(self.visual_widget)
        layout = QVBoxLayout()
        layout.addWidget(self.visual_widget)
        self.setLayout(layout)
        self.visual_widget.setFocus()
            
    
    def start_new_session(self):
        self.audio_engine.start()

    
    
    def _toggle_recording(self):
        """Start or stop recording"""
        pass
