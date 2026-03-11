"""
Note to color mapping
"""

from PySide6.QtGui import QColor


class ColorMapper:
    """Maps notes to colors"""
    
    def __init__(self):
        # E=0° anchor, 12 notes x 30° apart, keyed by MIDI pitch class (C=0)
        self.note_hues = {
            0: 240,   # C  = blue
            1: 270,   # C# = indigo
            2: 300,   # D  = purple
            3: 330,   # D# = pink-red
            4: 0,     # E  = red
            5: 30,    # F  = orange
            6: 60,    # F# = yellow-orange
            7: 90,    # G  = yellow
            8: 120,   # G# = yellow-green
            9: 150,   # A  = green
            10: 180,  # A# = teal
            11: 210,  # B  = cyan
        }

    def note_to_color(self, note_number: int, amplitude: float = 0.5) -> QColor:
        note = note_number % 12
        base_hue = self.note_hues[note]
        octave_note = note_number // 12
        octave_hue_shift = (octave_note - 2) * 12
        final_hue = (base_hue + octave_hue_shift) % 360
        saturation = 0.3 + (amplitude * 0.7)
        brightness = 0.9
        return QColor.fromHsvF(final_hue / 360, saturation, brightness)