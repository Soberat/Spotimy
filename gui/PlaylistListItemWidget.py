from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from Spotify import Playlist


class PlaylistListItemWidget(QWidget):

    selectedStyleSheet = "background-color:#346792"

    def __init__(self, playlist: Playlist):
        super().__init__()

        self.defaultStyleSheet = self.styleSheet()

        self.playlist = playlist

        self.imageLabel = QLabel()
        # self.imageLabel.setFixedWidth(30)
        self.imageLabel.setPixmap(QPixmap(playlist.image).scaled(30, 30, transformMode=Qt.SmoothTransformation))
        self.nameLabel = QLabel(playlist.name)
        self.nameLabel.setFont(QFont("ComicSans", 10, QFont.Bold))

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.imageLabel, alignment=Qt.AlignLeft)
        mainLayout.addWidget(self.nameLabel, alignment=Qt.AlignLeft)
        mainLayout.insertStretch(-1, 1)

        self.setFixedWidth(250)

    def selected(self):
        self.imageLabel.setStyleSheet(self.selectedStyleSheet)
        self.nameLabel.setStyleSheet(self.selectedStyleSheet)

    def deselected(self):
        self.imageLabel.setStyleSheet(self.defaultStyleSheet)
        self.nameLabel.setStyleSheet(self.defaultStyleSheet)
