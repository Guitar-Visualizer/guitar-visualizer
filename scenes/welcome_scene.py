from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class WelcomeScene(QWidget):
    start_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(48)
        self.setLayout(layout)

        title = QLabel("Guitar Visual Art")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Palatino", 72))
        title.setStyleSheet("color: #2d2d2d;")
        layout.addWidget(title)

        start_btn = QPushButton("Start")
        start_btn.setFixedSize(180, 52)
        start_btn.setFont(QFont("Palatino", 16))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2d2d2d;
                border: 1px solid #2d2d2d;
                border-radius: 26px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
                color: #f5f0e8;
            }
        """)
        start_btn.clicked.connect(self.start_clicked.emit)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
