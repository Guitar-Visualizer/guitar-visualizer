"""
audio/pitch_detector.py - Librosa with harmonic filtering
"""

import numpy as np
import librosa
from scipy.signal import find_peaks
from typing import List, Dict, Optional


class PitchDetector:
    """
    Detects single notes and chords from real-time guitar audio.

    Pipeline:
      1. Silence gate  — skip frames below RMS threshold
      2. Signal classifier — count non-harmonic spectral peaks to decide
         whether to route to single-note or chord detection first
      3. pyin  (monophonic, high accuracy) for single notes
         piptrack (polyphonic) for chords
      4. Cents-based harmonic filtering to remove overtones
      5. Deduplication by note name
      6. Chord identification with inversion awareness
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.min_freq = 75.0
        self.max_freq = 1400.0
        self.silence_threshold = 0.01
        self.pyin_confidence_threshold = 0.55
        self.chord_peak_threshold = 3
        self.harmonic_tolerance_cents = 20.0
        self.piptrack_magnitude_ratio = 0.12

        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                           'F#', 'G', 'G#', 'A', 'A#', 'B']

        self._chord_patterns = [
            (frozenset([0, 4, 7, 11]), "Major 7"),
            (frozenset([0, 3, 7, 10]), "Minor 7"),
            (frozenset([0, 4, 7, 10]), "Dominant 7"),
            (frozenset([0, 3, 6, 10]), "Half Diminished"),
            (frozenset([0, 3, 6, 9]),  "Diminished 7"),
            (frozenset([0, 4, 8, 10]), "Augmented 7"),
            (frozenset([0, 4, 7]),     "Major"),
            (frozenset([0, 3, 7]),     "Minor"),
            (frozenset([0, 3, 6]),     "Diminished"),
            (frozenset([0, 4, 8]),     "Augmented"),
            (frozenset([0, 5, 7]),     "Sus4"),
            (frozenset([0, 2, 7]),     "Sus2"),
            (frozenset([0, 7]),        "Power"),
        ]

    def detect_pitch(self, audio_data: np.ndarray) -> dict:
        audio_data = np.asarray(audio_data, dtype=np.float64).ravel()
        amplitude = self._rms(audio_data)
        if amplitude < self.silence_threshold:
            return self._empty_result(amplitude)

        is_chord_signal = self._classify_signal(audio_data)

        if is_chord_signal:
            result = self._detect_chord(audio_data, amplitude)
            if result is None:
                result = self._detect_single_note(audio_data, amplitude)
        else:
            result = self._detect_single_note(audio_data, amplitude)
            if result is None:
                result = self._detect_chord(audio_data, amplitude)

        return result if result is not None else self._empty_result(amplitude)

    def _classify_signal(self, audio_data: np.ndarray) -> bool:
        n_fft = min(2048, len(audio_data))
        frame = np.zeros(n_fft)
        frame[:min(n_fft, len(audio_data))] = audio_data[:n_fft]
        window = np.hanning(n_fft)
        spectrum = np.abs(np.fft.rfft(frame * window))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / self.sample_rate)

        valid_mask = (freqs >= self.min_freq) & (freqs <= self.max_freq)
        sub_spectrum = spectrum[valid_mask]
        sub_freqs = freqs[valid_mask]

        if len(sub_spectrum) == 0:
            return False

        max_val = np.max(sub_spectrum)
        if max_val == 0:
            return False

        peak_indices, _ = find_peaks(
            sub_spectrum,
            height=max_val * 0.08,
            prominence=max_val * 0.04,
            distance=3,
        )

        if len(peak_indices) < 2:
            return False

        peaks = [
            {'frequency': float(sub_freqs[i]), 'magnitude': float(sub_spectrum[i])}
            for i in peak_indices
        ]

        fundamentals = self._remove_harmonics_cents(peaks)
        return len(fundamentals) >= self.chord_peak_threshold

    def _detect_single_note(self, audio_data: np.ndarray, amplitude: float) -> Optional[dict]:
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_data,
                fmin=self.min_freq,
                fmax=self.max_freq,
                sr=self.sample_rate,
                fill_na=None,
            )
        except Exception:
            return None

        if voiced_flag is None or not np.any(voiced_flag):
            return None

        valid_pitches = f0[voiced_flag]
        valid_probs = voiced_probs[voiced_flag]

        nan_mask = ~np.isnan(valid_pitches)
        valid_pitches = valid_pitches[nan_mask]
        valid_probs = valid_probs[nan_mask]

        if len(valid_pitches) == 0:
            return None

        best_idx = int(np.argmax(valid_probs))
        frequency = float(valid_pitches[best_idx])
        confidence = float(valid_probs[best_idx])

        if confidence < self.pyin_confidence_threshold:
            return None

        if not (self.min_freq <= frequency <= self.max_freq):
            return None

        note_info = self._frequency_to_note(frequency)
        return self._build_result(
            is_chord=False,
            notes=[note_info],
            amplitude=amplitude,
            confidence=confidence,
        )

    def _detect_chord(self, audio_data: np.ndarray, amplitude: float) -> Optional[dict]:
        n_fft = min(4096, len(audio_data))
        try:
            pitches, magnitudes = librosa.piptrack(
                y=audio_data,
                sr=self.sample_rate,
                n_fft=n_fft,
                fmin=self.min_freq,
                fmax=self.max_freq,
                threshold=0.05,
            )
        except Exception:
            return None

        detected = self._extract_strong_pitches(pitches, magnitudes)
        if not detected:
            return None

        filtered = self._remove_harmonics_cents(detected)
        if not filtered:
            return None

        filtered = self._deduplicate_by_note_name(filtered)
        filtered.sort(key=lambda x: x['frequency'])
        filtered = filtered[:6]

        is_chord = len(filtered) >= 2

        return self._build_result(
            is_chord=is_chord,
            notes=filtered,
            amplitude=amplitude,
            confidence=0.65 if is_chord else 0.55,
        )

    def _extract_strong_pitches(self, pitches, magnitudes):
        max_magnitude = float(np.max(magnitudes))
        if max_magnitude == 0:
            return []

        threshold = max_magnitude * self.piptrack_magnitude_ratio
        detected = []

        for t in range(magnitudes.shape[1]):
            col_mags = magnitudes[:, t]
            col_pitches = pitches[:, t]

            valid = (col_pitches > self.min_freq) & (col_pitches <= self.max_freq)
            if not np.any(valid):
                continue

            valid_indices = np.where(valid)[0]
            top_n = min(4, len(valid_indices))
            top_indices = valid_indices[
                np.argsort(col_mags[valid_indices])[::-1][:top_n]
            ]

            for idx in top_indices:
                mag = float(col_mags[idx])
                freq = float(col_pitches[idx])
                if mag >= threshold:
                    note_info = self._frequency_to_note(freq)
                    note_info['magnitude'] = mag
                    detected.append(note_info)

        return detected

    def _remove_harmonics_cents(self, notes: List[Dict]) -> List[Dict]:
        if len(notes) <= 1:
            return list(notes)

        sorted_notes = sorted(notes, key=lambda x: x.get('magnitude', 1.0), reverse=True)
        keep: List[Dict] = []

        for note in sorted_notes:
            freq = note['frequency']
            if freq <= 0:
                continue

            is_harmonic = False
            for fundamental in keep:
                fund_freq = fundamental['frequency']
                if fund_freq <= 0:
                    continue
                for h in range(2, 9):
                    harmonic_freq = fund_freq * h
                    cents_diff = abs(1200.0 * np.log2(freq / harmonic_freq))
                    if cents_diff < self.harmonic_tolerance_cents:
                        is_harmonic = True
                        break
                if is_harmonic:
                    break

            if not is_harmonic:
                keep.append(note)

        return keep

    def _deduplicate_by_note_name(self, notes: List[Dict]) -> List[Dict]:
        seen: Dict[str, Dict] = {}
        for note in notes:
            name = note['note']
            if name not in seen or note.get('magnitude', 0.0) > seen[name].get('magnitude', 0.0):
                seen[name] = note
        return list(seen.values())

    def identify_chord(self, note_numbers: List[int]) -> Optional[str]:
        if len(note_numbers) < 2:
            return None

        pitch_classes = sorted(set(n % 12 for n in note_numbers))
        if len(pitch_classes) < 2:
            return None

        for root in pitch_classes:
            intervals = frozenset((pc - root) % 12 for pc in pitch_classes)
            for pattern, name in self._chord_patterns:
                if pattern == intervals:
                    return f"{self.note_names[root]} {name}"

        sorted_patterns = sorted(self._chord_patterns, key=lambda x: len(x[0]), reverse=True)
        for root in pitch_classes:
            intervals = frozenset((pc - root) % 12 for pc in pitch_classes)
            for pattern, name in sorted_patterns:
                if pattern.issubset(intervals):
                    return f"{self.note_names[root]} {name}"

        root_name = self.note_names[pitch_classes[0]]
        note_list = [self.note_names[pc] for pc in pitch_classes]
        return f"{root_name} ({', '.join(note_list)})"

    def _build_result(self, is_chord, notes, amplitude, confidence):
        chord_name = self.identify_chord([n['note_number'] for n in notes]) if is_chord else None

        return {
            'has_note':     True,
            'is_chord':     is_chord,
            'chord_name':   chord_name,
            'notes':        [n['note'] for n in notes],
            'note_names':   [n['note_name'] for n in notes],
            'note_numbers': [n['note_number'] for n in notes],
            'frequencies':  [n['frequency'] for n in notes],
            'note':         notes[0]['note'],
            'note_name':    notes[0]['note_name'],
            'note_number':  notes[0]['note_number'],
            'frequency':    notes[0]['frequency'],
            'amplitude':    float(amplitude),
            'confidence':   float(confidence),
        }

    def _empty_result(self, amplitude: float) -> dict:
        return {
            'has_note':     False,
            'is_chord':     False,
            'chord_name':   None,
            'notes':        [],
            'note_names':   [],
            'note_numbers': [],
            'frequencies':  [],
            'note':         None,
            'note_name':    None,
            'note_number':  None,
            'frequency':    0.0,
            'amplitude':    float(amplitude),
            'confidence':   0.0,
        }

    def _rms(self, audio_data: np.ndarray) -> float:
        return float(np.sqrt(np.mean(audio_data ** 2)))

    def _frequency_to_note(self, frequency: float) -> Dict:
        semitones_from_a4 = 12.0 * np.log2(frequency / 440.0)
        note_number = int(round(69 + semitones_from_a4))
        octave = (note_number // 12) - 1
        note_index = note_number % 12
        note_name = self.note_names[note_index]
        return {
            'note':        f"{note_name}{octave}",
            'note_name':   note_name,
            'note_number': note_number,
            'octave':      octave,
            'frequency':   float(frequency),
            'magnitude':   0.0,
        }