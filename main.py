#!/usr/bin/env python3
"""
Guitar Visual Art Generator
Main entry point
"""
import signal
import sys
from PySide6.QtWidgets import QApplication
from core.app import GuitarVisualApp


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setApplicationName("Guitar Visual Art")
    
    window = GuitarVisualApp()
    window.showFullScreen()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
