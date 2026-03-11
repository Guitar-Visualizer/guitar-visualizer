"""
Audio capture and processing
"""
import numpy as np
import sounddevice as sd
from PySide6.QtCore import Signal, QObject, Qt
from audio.technique_detector import TechniqueDetector
from audio.pitch_detector import PitchDetector


class AudioProcessor(QObject):
    """Audio processor - runs sounddevice stream directly"""
    audio_analyzed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.technique_detector = TechniqueDetector()
        self.pitch_detector = PitchDetector()
        self.stream = None

    def start(self):
        print("AudioProcessor.start() called")
        try:
            self.stream = sd.InputStream(
                samplerate=44100,
                channels=1,
                dtype='float32',
                blocksize=4096,
                callback=self._audio_callback
            )
            self.stream.start()
            print("Audio stream started successfully")
        except Exception as e:
            print(f"Audio stream error: {e}")

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        try:
            audio_data = indata[:, 0].astype(np.float64).copy()
            pitch_result = self.pitch_detector.detect_pitch(audio_data)
            audio_result = self.technique_detector.detect_technique(audio_data, pitch_result)
            pitch_result['technique'] = audio_result
            # safely emit signal from sounddevice thread to Qt main thread
            self.audio_analyzed.emit(pitch_result)
        except Exception as e:
            print(f"Callback error: {e}")


class AudioEngine:
    """Main audio engine"""

    def __init__(self, visual_widget):
        self.visual_widget = visual_widget
        self.processor = AudioProcessor()
        self.processor.audio_analyzed.connect(
            self.visual_widget.on_audio_event,
            Qt.ConnectionType.QueuedConnection  # safe cross-thread signal
        )

    def start(self):
        print("AudioEngine.start() called")
        self.processor.start()

    def stop(self):
        self.processor.stop()