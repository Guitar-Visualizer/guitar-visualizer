"""
Audio capture and processing
"""
import sounddevice as sd
from PySide6.QtCore import QThread, Signal, QObject
from audio.technique_detector import TechniqueDetector
from audio.pitch_detector import PitchDetector


class AudioProcessor(QObject):
    """Audio processor running in separate thread"""
    
    audio_analyzed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.technique_detector = TechniqueDetector()
        self.pitch_detector = PitchDetector()
       
    
    def start(self):
        
        self.stream = sd.InputStream(
            samplerate=44100,
            channels=1,
            dtype='float32',
            blocksize=4096,
            callback=self._audio_callback)
        self.stream.start()
        
    def stop(self):  
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def _process_audio(self, audio_data):   
        pitch_result = self.pitch_detector.detect_pitch(audio_data)
        audio_result = self.technique_detector.detect_technique(audio_data, pitch_result)
        pitch_result['technique'] = audio_result
        print(f"has_note: {pitch_result['has_note']}, amplitude: {pitch_result['amplitude']:.4f}")
        self.audio_analyzed.emit(pitch_result)

        
    def _audio_callback(self, indata, frames, time, status):
        audio_data = indata[:, 0]  # get mono channel
        self._process_audio(audio_data)
class AudioEngine:
    
    def __init__(self, visual_widget):
        self.visual_widget = visual_widget
        self.thread = QThread()
        self.processor = AudioProcessor()
        self.processor.moveToThread(self.thread)  # move processor to background thread
        self.thread.started.connect(self.processor.start)  # start processor when thread starts
        self.processor.audio_analyzed.connect(self.visual_widget.on_audio_event)  # connect signal
            
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.processor.stop()
        self.thread.quit()
