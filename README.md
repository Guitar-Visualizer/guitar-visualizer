

```
guitar_visual_art/
├── main.py                    # Entry point
├── audio/                     # Audio capture & analysis
│   ├── audio_engine.py       # Main audio coordinator
│   ├── pitch_detector.py     # Pitch detection
│   └── technique_detector.py # Technique detection
├── config/                    # Settings
│   ├── color_mapping.py      # Note-to-color
│   └── settings.py           # App config
├── core/                      # Core app logic
│   ├── app.py               # Main window
│   └── project_manager.py   # Session management
├── scenes/                    # UI screens
│   ├── welcome_scene.py     # Welcome screen
│   ├── gallery_scene.py     # Session gallery
│   └── visualizer_scene.py  # Recording scene
├── session/                   # Recording
│   └── recorder.py          # Audio/video capture
├── visuals/                   # Visual effects
│   ├── visual_widget.py     # Canvas
│   └── effects/             # Effect classes
└── projects/                  # Saved sessions
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Next Steps

Each file has `# TODO` comments showing what needs to be implemented.
Start with the core app flow, then add audio processing, then visuals.
