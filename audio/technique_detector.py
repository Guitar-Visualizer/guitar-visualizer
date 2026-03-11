"""
Guitar technique detection
"""

import numpy as np


class TechniqueDetector:
    """Detects guitar techniques"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.pitch_history = []
    
    def detect_technique(self, audio_data: np.ndarray, pitch_info: dict) -> dict:
        """
        Detect playing technique
        
        Returns:
            dict with: technique ('normal', 'vibrato', 'slide', 'hammer_on', 'bend')
        """
        note_number = pitch_info['note_number']
        amplitude = pitch_info['amplitude']
        
        self.pitch_history.append({'note_number': note_number, 'amplitude': amplitude})
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
    def _detect_hammer_on(self):
        if len(self.pitch_history) < 2:
            return False
        old_note = self.pitch_history[-2]
        new_note = self.pitch_history[-1]
        old_note_number = old_note['note_number']
        new_note_number = new_note['note_number']
        semi_tone_diff = new_note_number - old_note_number
        if 1 <= semi_tone_diff <= 5:
            if new_note['amplitude'] <= 0.4:
                return True
        return False
    # TODO: Detect bend (pitch deviation)
    def _detect_pull_off(self):
        if len(self.pitch_history) <2:
            return False
        old_note = self.pitch_history[-2]
        new_note = self.pitch_history[-1]
        old_note_number = old_note['note_number']
        new_note_number = new_note['note_number']
        semi_tone_diff = old_note_number - new_note_number
        if 1 <= semi_tone_diff <= 5:
            if new_note['amplitude'] <= 0.4:
                return True
        return False
    
    def _detect_slide(self):
        if len(self.pitch_history) < 5:
            return False
        frames = self.pitch_history[-5:]
        steps = []
        for i in range(1, len(frames)):
            diff = frames[i]['note_number'] - frames[i-1]['note_number']
            steps.append(diff)
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
        if len(self.pitch_history) < 10:
            return False
        frames = self.pitch_history[-10:]
        rising_frames = frames[:5]
        stable_frames = frames[5:]
        rising_steps = []
        stable_steps = []
        for i in range(1, len(rising_frames)):
            diff = rising_frames[i]['note_number'] - rising_frames[i-1]['note_number']
            rising_steps.append(diff)
        gradual = all(abs(s) <= 2 for s in rising_steps)
        going_up = all(s > 0 for s in rising_steps)
        for i in range(1, len(stable_frames)):
            diff = stable_frames[i]['note_number'] - stable_frames[i-1]['note_number']
            stable_steps.append(diff)
        total = sum(abs(s) for s in stable_steps)
        stable = all(s <= 1 for s in stable_steps)
        total_rise = sum(rising_steps)

        if gradual and going_up and stable and 1 <= total_rise <=3:
            return 'bend'
        return False
    
    def _detect_vibrato(self):
        if len(self.pitch_history) < 15:
            return False
        frames = self.pitch_history[-15:]
        steps = []
        for i in range(1, len(frames)):
            diff = frames[i]['note_number'] - frames[i-1]['note_number']
            steps.append(diff)
        alternating = all(steps[i] * steps[i+1] < 0 for i in range(len(steps)-1))
        small_steps = all(abs(s) <= 1 for s in steps)
        if alternating and small_steps:
            return 'vibrato'
        return False
    