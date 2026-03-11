from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                                QGridLayout, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class SessionCard(QFrame):
    clicked = Signal(str)

    def __init__(self, session_name: str, session_date: str, session_id: str):
        super().__init__()
        self.session_id = session_id
        self.setFixedSize(320, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: #ede8df;
                border: none;
                border-radius: 4px;
            }
            QFrame:hover {
                background-color: #e0dbd0;
            }
        """)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        self.setLayout(layout)

        name_label = QLabel(session_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setFont(QFont("Palatino", 18))
        name_label.setStyleSheet("color: #2d2d2d; background: transparent;")
        layout.addWidget(name_label)

        date_label = QLabel(session_date)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setFont(QFont("Palatino", 11))
        date_label.setStyleSheet("color: #888077; background: transparent;")
        layout.addWidget(date_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.session_id)


class NewSessionCard(QFrame):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(320, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1px solid #b0aa9f;
                border-radius: 4px;
            }
            QFrame:hover {
                border: 1px solid #2d2d2d;
            }
        """)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        self.setLayout(layout)

        plus_label = QLabel("+")
        plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plus_label.setFont(QFont("Palatino", 40))
        plus_label.setStyleSheet("color: #b0aa9f; border: none;")
        layout.addWidget(plus_label)

        text_label = QLabel("New Session")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setFont(QFont("Palatino", 14))
        text_label.setStyleSheet("color: #b0aa9f; border: none;")
        layout.addWidget(text_label)

    def mousePressEvent(self, event):
        self.clicked.emit()


class GalleryScene(QWidget):
    new_session_requested = Signal()
    session_selected = Signal(str)

    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        self.setStyleSheet("background-color: #f5f0e8;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(80, 80, 80, 80)
        main_layout.setSpacing(48)
        self.setLayout(main_layout)

        title = QLabel("Your Visual Sessions")
        title.setFont(QFont("Palatino", 42))
        title.setStyleSheet("color: #2d2d2d; background: transparent;")
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(28)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_widget.setLayout(self.grid_layout)

        scroll.setWidget(self.grid_widget)
        main_layout.addWidget(scroll)

        self.refresh_gallery()

    def refresh_gallery(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        new_card = NewSessionCard()
        new_card.clicked.connect(self.new_session_requested.emit)
        self.grid_layout.addWidget(new_card, 0, 0)

        sessions = self._load_sessions()
        for i, session in enumerate(sessions):
            card = SessionCard(session['name'], session['date'], session['id'])
            card.clicked.connect(self.session_selected.emit)
            row = (i + 1) // 3
            col = (i + 1) % 3
            self.grid_layout.addWidget(card, row, col)

    def _load_sessions(self):
        return []
