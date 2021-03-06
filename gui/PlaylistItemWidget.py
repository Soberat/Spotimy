import datetime
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from CachingImageGetter import get_image
from Spotify import PlaylistTrack


# TODO: Animate index when track is playing, color title green


class PlaylistItemWidget(QWidget):

    selectedStyleSheet = "background-color:#5A5A5A;"
    albumCoverSize = 40

    playTrack = pyqtSignal(str)

    def __init__(self, playlistTrack: PlaylistTrack):
        super().__init__()

        self.playlistTrack = playlistTrack

        self.defaultStyleSheet = self.styleSheet()

        self.indexLabel: QLabel = QLabel(str(playlistTrack.index))
        self.indexLabel.setFixedWidth(25)
        self.indexLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel: QLabel = QLabel()
        if playlistTrack.track.albumCoverUri is not None:
            self.coverLabel.setPixmap(
                get_image(playlistTrack.track.albumCoverUri).scaled(self.albumCoverSize, self.albumCoverSize, transformMode=Qt.SmoothTransformation))
        else:
            self.coverLabel.setPixmap(
                QPixmap(':/track_placeholder.png').scaled(self.albumCoverSize, self.albumCoverSize, transformMode=Qt.SmoothTransformation))
        self.titleLabel = QLabel(playlistTrack.track.title)
        self.titleLabel.setFont(QFont("Gotham Book", 9, QFont.Bold))
        self.titleLabel.setStyleSheet("color: #FFFFFF;")
        self.artistsLabel = QLabel(', '.join(playlistTrack.track.artists))
        self.artistsLabel.setFont(QFont("Gotham Book", 9, QFont.Normal))
        self.albumLabel = QLabel(playlistTrack.track.album)
        self.albumLabel.setFixedWidth(400)

        time = datetime.datetime.strptime(playlistTrack.addedAt, "%Y-%m-%dT%H:%M:%SZ")
        delta = datetime.datetime.now() - time

        # Format date the same way Spotify does
        if delta.days > 31:
            self.addedLabel = QLabel(time.strftime("%d %b %Y"))
        elif delta.days > 0:
            self.addedLabel = QLabel(f"{delta.days} days ago")
        elif delta.seconds/3600 > 0:
            self.addedLabel = QLabel(f"{int(delta.seconds/3600)} hours ago")
        elif delta.seconds/60 > 0:
            self.addedLabel = QLabel(f"{int(delta.seconds/60)} minutes ago")
        else:
            self.addedLabel = QLabel(f"{delta.seconds} seconds ago")
        self.addedLabel.setFixedWidth(350)

        time = playlistTrack.track.runtime / 1000
        minutes = int(time / 60)
        seconds = int(time - 60 * minutes)
        self.runtimeLabel = QLabel(f"{minutes:02d}:{seconds:02d}")
        self.runtimeLabel.setFixedWidth(60)

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.indexLabel, alignment=Qt.AlignLeft)
        mainLayout.addWidget(self.coverLabel, alignment=Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.addStretch(100)
        layout.addWidget(self.titleLabel)
        innerLayout = QHBoxLayout()
        # TODO: Insert status od download and sync?
        innerLayout.addWidget(self.artistsLabel)
        layout.addLayout(innerLayout)
        layout.addStretch(100)

        mainLayout.addLayout(layout)

        mainLayout.addWidget(self.albumLabel, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.addedLabel, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.runtimeLabel, alignment=Qt.AlignCenter)

        mainLayout.setStretch(2, 100)

    def selected(self):
        self.indexLabel.setStyleSheet(self.selectedStyleSheet)
        self.coverLabel.setStyleSheet(self.selectedStyleSheet)
        self.titleLabel.setStyleSheet(self.selectedStyleSheet + "color: #FFFFFF;")
        self.artistsLabel.setStyleSheet(self.selectedStyleSheet)
        self.albumLabel.setStyleSheet(self.selectedStyleSheet)
        self.addedLabel.setStyleSheet(self.selectedStyleSheet)
        self.runtimeLabel.setStyleSheet(self.selectedStyleSheet)

    def deselected(self):
        self.indexLabel.setStyleSheet(self.defaultStyleSheet)
        self.coverLabel.setStyleSheet(self.defaultStyleSheet)
        self.titleLabel.setStyleSheet(self.defaultStyleSheet + "color: #FFFFFF;")
        self.artistsLabel.setStyleSheet(self.defaultStyleSheet)
        self.albumLabel.setStyleSheet(self.defaultStyleSheet)
        self.addedLabel.setStyleSheet(self.defaultStyleSheet)
        self.runtimeLabel.setStyleSheet(self.defaultStyleSheet)

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        self.playTrack.emit(self.playlistTrack.track.trackUri)
