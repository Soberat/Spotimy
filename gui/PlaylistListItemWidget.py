from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from CachingImageGetter import get_image
from Spotify import Playlist


class PlaylistListItemWidget(QWidget):

    selectedStyleSheet = "QLabel {color: #FFFFFF}"
    playPlaylist = pyqtSignal(Playlist)

    def __init__(self, playlist: Playlist):
        super().__init__()

        self.defaultStyleSheet = self.styleSheet()
        self.isSelected = False
        self.playlist = playlist

        self.imageLabel = QLabel()
        if playlist.image is not None:
            self.imageLabel.setPixmap(get_image(playlist.image).scaled(45, 45, transformMode=Qt.SmoothTransformation))
        else:
            self.imageLabel.setPixmap(QPixmap(':/playlist_placeholder.png').scaled(45, 45, transformMode=Qt.SmoothTransformation))
        self.nameLabel = QLabel(playlist.name)
        self.nameLabel.setFont(QFont("ComicSans", 10, QFont.Bold))

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.imageLabel, alignment=Qt.AlignLeft)
        mainLayout.addWidget(self.nameLabel, alignment=Qt.AlignLeft)
        mainLayout.insertStretch(-1, 1)

        self.setFixedWidth(250)

    def event(self, event):
        if not self.isSelected:
            if event.type() == QEvent.HoverEnter:
                self.nameLabel.setStyleSheet("QLabel {color: #FFFFFF}")
            elif event.type() == QEvent.HoverLeave:
                self.nameLabel.setStyleSheet(self.defaultStyleSheet)
        return super().event(event)

    def selected(self):
        self.isSelected = True
        self.nameLabel.setStyleSheet(self.selectedStyleSheet)

    def deselected(self):
        self.isSelected = False
        self.nameLabel.setStyleSheet(self.defaultStyleSheet)

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        self.playPlaylist.emit(self.playlist)
