from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout


class LabeledIconButton(QFrame):
    clicked = pyqtSignal()

    def __init__(self, text: str, pixmapPath: str):
        super().__init__()

        self.defaultStyleSheet = self.styleSheet()

        self.iconLabel = QLabel()
        self.iconLabel.setPixmap(QPixmap(pixmapPath).scaled(24, 24, transformMode=Qt.SmoothTransformation))

        self.textLabel = QLabel(text)
        font = self.textLabel.font()
        font.setBold(True)
        font.setPointSize(10)
        self.textLabel.setFont(font)

        layout = QHBoxLayout()
        layout.addWidget(self.iconLabel)
        layout.addWidget(self.textLabel, alignment=Qt.AlignVCenter)
        layout.setStretch(1, 100)

        self.setLayout(layout)

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            self.iconLabel.setStyleSheet("QLabel {color: #FFFFFF}")
            self.textLabel.setStyleSheet("QLabel {color: #FFFFFF}")
        elif event.type() == QEvent.HoverLeave:
            self.iconLabel.setStyleSheet(self.defaultStyleSheet)
            self.textLabel.setStyleSheet(self.defaultStyleSheet)
        return super().event(event)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()