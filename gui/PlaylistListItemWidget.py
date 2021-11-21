from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from CachingImageGetter import get_image
from Spotify import Playlist
import resources

class PlaylistListItemWidget(QWidget):

    selectedStyleSheet = "background-color:#346792"

    def __init__(self, playlist: Playlist):
        super().__init__()

        self.defaultStyleSheet = self.styleSheet()

        self.playlist = playlist

        self.imageLabel = QLabel()
        if playlist.image is not None:
            self.imageLabel.setPixmap(get_image(playlist.image).scaled(60, 60, transformMode=Qt.SmoothTransformation))
        else:
            self.imageLabel.setPixmap(QPixmap('playlist_placeholder.png').scaled(60, 60, transformMode=Qt.SmoothTransformation))
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
