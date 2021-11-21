from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from CachingImageGetter import get_image
from Spotify import Track
import resources

class PlaylistItemWidget(QWidget):

    selectedStyleSheet = "background-color:#346792"

    def __init__(self, track: Track):
        super().__init__()

        self.track = track

        self.defaultStyleSheet = self.styleSheet()

        self.indexLabel: QLabel = QLabel(str(track.index))
        self.indexLabel.setFixedWidth(25)
        self.indexLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel: QLabel = QLabel()
        if track.albumCoverUri is not None:
            self.coverLabel.setPixmap(
                get_image(track.albumCoverUri).scaled(35, 35, transformMode=Qt.SmoothTransformation))
        else:
            self.coverLabel.setPixmap(
                QPixmap('track_placeholder.png').scaled(35, 35, transformMode=Qt.SmoothTransformation))
        self.titleLabel = QLabel(track.title)
        self.titleLabel.setFixedWidth(400)
        self.titleLabel.setFont(QFont("Gotham Book", 9, QFont.Bold))
        self.artistsLabel = QLabel(', '.join(track.artists))
        self.artistsLabel.setFont(QFont("Gotham Book", 9, QFont.Normal))
        self.albumLabel = QLabel(track.album)
        self.albumLabel.setFixedWidth(400)
        self.addedLabel = QLabel(track.added)
        self.addedLabel.setFixedWidth(350)

        time = track.runtime / 1000
        minutes = int(time / 60)
        seconds = int(time - 60 * minutes)
        self.runtimeLabel = QLabel(f"{minutes:02d}:{seconds:02d}")
        self.runtimeLabel.setFixedWidth(60)

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.indexLabel, alignment=Qt.AlignLeft)
        mainLayout.addWidget(self.coverLabel, alignment=Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.addWidget(self.titleLabel)
        innerLayout = QHBoxLayout()
        # TODO: Insert status od download and sync?
        innerLayout.addWidget(self.artistsLabel)
        layout.addLayout(innerLayout)
        mainLayout.addLayout(layout)

        mainLayout.addWidget(self.albumLabel, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.addedLabel, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.runtimeLabel, alignment=Qt.AlignCenter)

        mainLayout.setStretch(2, 100)

    def selected(self):
        self.indexLabel.setStyleSheet(self.selectedStyleSheet)
        self.coverLabel.setStyleSheet(self.selectedStyleSheet)
        self.titleLabel.setStyleSheet(self.selectedStyleSheet)
        self.artistsLabel.setStyleSheet(self.selectedStyleSheet)
        self.albumLabel.setStyleSheet(self.selectedStyleSheet)
        self.addedLabel.setStyleSheet(self.selectedStyleSheet)
        self.runtimeLabel.setStyleSheet(self.selectedStyleSheet)

    def deselected(self):
        self.indexLabel.setStyleSheet(self.defaultStyleSheet)
        self.coverLabel.setStyleSheet(self.defaultStyleSheet)
        self.titleLabel.setStyleSheet(self.defaultStyleSheet)
        self.artistsLabel.setStyleSheet(self.defaultStyleSheet)
        self.albumLabel.setStyleSheet(self.defaultStyleSheet)
        self.addedLabel.setStyleSheet(self.defaultStyleSheet)
        self.runtimeLabel.setStyleSheet(self.defaultStyleSheet)
