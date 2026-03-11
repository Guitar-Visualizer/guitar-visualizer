import numpy as np

class TechniqueDetector:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.pitch_history = []

    def detect_technique(self, audio_data: np.ndarray, pitch_info: dict) -> str:
        if not pitch_info['has_note']:
            self.pitch_history.clear()
            return 'normal'
        note_number = pitch_info['note_number']
        amplitude = pitch_info['amplitude']
        if note_number is None or amplitude is None:
            self.pitch_history.clear()
            return 'normal'
        self.pitch_history.append({'note_number': int(note_number), 'amplitude': float(amplitude)})
        self.pitch_history = [f for f in self.pitch_history if f['note_number'] is not None]
        self.pitch_history = self.pitch_history[-20:]
        if self._detect_hammer_on():
            return 'hammer_on'
        if self._detect_pull_off():
            return 'pull_off'
        if self._detect_bend():
            return 'bend'
        slide = self._detect_slide()
        if slide:
            return slide
        if self._detect_vibrato():
            return 'vibrato'
        return 'normal'

    def _safe_history(self, n):
        valid = [f for f in self.pitch_history if isinstance(f['note_number'], int)]
        return valid[-n:] if len(valid) >= n else []

    def _detect_hammer_on(self):
        frames = self._safe_history(2)
        if len(frames) < 2:
            return False
        diff = frames[-1]['note_number'] - frames[-2]['note_number']
        if 1 <= diff <= 5:
            if frames[-1]['amplitude'] <= 0.4:
                return True
        return False

    def _detect_pull_off(self):
        frames = self._safe_history(2)
        if len(frames) < 2:
            return False
        diff = frames[-2]['note_number'] - frames[-1]['note_number']
        if 1 <= diff <= 5:
            if frames[-1]['amplitude'] <= 0.4:
                return True
        return False

    def _detect_slide(self):
        frames = self._safe_history(5)
        if len(frames) < 5:
            return False
        steps = [frames[i]['note_number'] - frames[i-1]['note_number'] for i in range(1, len(frames))]
        gradual = all(abs(s) <= 2 for s in steps)
        going_up = all(s > 0 for s in steps)
        going_down = all(s < 0 for s in steps)
        total = sum(abs(s) for s in steps)
        if gradual and going_up and total > 2:
            return 'slide_up'
        if gradual and going_down and total > 2:
            return 'slide_down'
        return False

    def _detect_bend(self):
        frames = self._safe_history(10)
        if len(frames) < 10:
            return False
        rising_frames = frames[:5]
        stable_frames = frames[5:]
        rising_steps = [rising_frames[i]['note_number'] - rising_frames[i-1]['note_number'] for i in range(1, len(rising_frames))]
        stable_steps = [stable_frames[i]['note_number'] - stable_frames[i-1]['note_number'] for i in range(1, len(stable_frames))]
        gradual = all(abs(s) <= 2 for s in rising_steps)
        going_up = all(s > 0 for s in rising_steps)
        stable = all(abs(s) <= 1 for s in stable_steps)
        total_rise = sum(rising_steps)
        if gradual and going_up and stable and 1 <= total_rise <= 3:
            return 'bend'
        return False

    def _detect_vibrato(self):
        frames = self._safe_history(15)
        if len(frames) < 15:
            return False
        steps = [frames[i]['note_number'] - frames[i-1]['note_number'] for i in range(1, len(frames))]
        alternating = all(steps[i] * steps[i+1] < 0 for i in range(len(steps)-1))
        small_steps = all(abs(s) <= 1 for s in steps)
        if alternating and small_steps:
            return 'vibrato'
        return False
