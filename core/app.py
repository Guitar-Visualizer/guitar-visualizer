from PySide6.QtWidgets import QMainWindow, QStackedWidget
from scenes.welcome_scene import WelcomeScene
from scenes.gallery_scene import GalleryScene
from scenes.visualizer_scene import VisualizerScene


class GuitarVisualApp(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guitar Visual Art")
        self.setMinimumSize(1024, 768)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.stack.setStyleSheet("background-color: #f5f0e8;")

        # initialize scenes
        self.welcome = WelcomeScene()
        self.gallery = GalleryScene(project_manager=None)
        self.visualizer = VisualizerScene(project_manager=None)

        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.gallery)
        self.stack.addWidget(self.visualizer)

        # wire signals
        self.welcome.start_clicked.connect(self.show_gallery)
        self.gallery.new_session_requested.connect(self.start_new_session)

        # start on welcome screen
        self.stack.setCurrentWidget(self.welcome)

    def show_gallery(self):
        self.gallery.refresh_gallery()
        self.stack.setCurrentWidget(self.gallery)

    def start_new_session(self):
        self.stack.setCurrentWidget(self.visualizer)
        self.visualizer.start_new_session()
