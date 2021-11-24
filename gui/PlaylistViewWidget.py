# Widget presenting the playlist in a similar way Spotify does

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QImage, QBitmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QListWidgetItem, QSplitter

import CachingImageGetter
from CachingImageGetter import get_image
from Spotify import Playlist
from gui.PlaylistItemWidget import PlaylistItemWidget
from gui.TrackListWidget import TrackListWidget
import resources

# TODO: Add "Move to index" context menu option
# TODO: Split header info string into multiple labels
# TODO: Add gradient as background


class PlaylistViewWidget(QWidget):

    playTrack = pyqtSignal(str, str)

    def __init__(self, playlist: Playlist):
        super().__init__()
        self.playlist = playlist
        self.totalRuntime = 0
        self.previousSelection = set()

        self.mainLayout = QVBoxLayout()

        self.coverLabel = QLabel()
        self.coverLabel.setStyleSheet("background: #282828;")
        if playlist.image is not None:
            self.coverLabel.setPixmap(get_image(playlist.image).scaled(192, 192, transformMode=Qt.SmoothTransformation))
        else:
            self.coverLabel.setPixmap(
                QPixmap(':/playlist_placeholder.png').scaled(192, 192, transformMode=Qt.SmoothTransformation))
        # Font: Vision - Free Font Family
        self.nameLabel = QLabel(playlist.name)
        self.nameLabel.setFont(QFont('Gotham', 36, QFont.Black))
        self.nameLabel.setStyleSheet("QLabel {color: #FFFFFF;}")

        self.ownerPictureLabel = QLabel()
        self.ownerPictureLabel.setFixedHeight(40)
        if playlist.ownerPicture is not None:
            picture = CachingImageGetter.get_image(playlist.ownerPicture).scaled(512, 512,
                                                                                 transformMode=Qt.SmoothTransformation)
        else:
            picture = QPixmap(':/pfp_placeholder.png').scaled(512, 512)
        mask = QImage(':/pfp_mask.png').createAlphaMask()
        picture.setMask(QBitmap.fromImage(mask))
        self.ownerPictureLabel.setPixmap(picture.scaled(30, 30, transformMode=Qt.SmoothTransformation))

        self.infoLabel = QLabel()
        self.infoLabel.setFont(QFont('Gotham', 12, QFont.Normal))
        self.infoLabel.setFixedHeight(40)

        self.trackList = TrackListWidget()

        headerLayout = QHBoxLayout()
        headerLayout.addWidget(self.coverLabel, alignment=Qt.AlignBottom)

        layout = QVBoxLayout()
        layout.addWidget(self.nameLabel, alignment=Qt.AlignHCenter)
        innerLayout = QHBoxLayout()
        innerLayout.addWidget(self.ownerPictureLabel, alignment=Qt.AlignBottom)
        innerLayout.addWidget(self.infoLabel, alignment=Qt.AlignBottom)
        innerLayout.setStretch(1, 10)

        layout.addLayout(innerLayout)

        headerLayout.addLayout(layout)
        headerLayout.setStretch(1, 10)

        self.mainLayout.addLayout(headerLayout)
        self.mainLayout.addWidget(QSplitter(Qt.Horizontal))
        self.mainLayout.addWidget(self.trackList)
        self.mainLayout.setStretch(2, 10)

        self.setLayout(self.mainLayout)
        self.setMinimumSize(500, 500)

        self.trackList.itemSelectionChanged.connect(self.list_selection_changed)
        # Override default stylesheet to show selected items
        self.trackList.setStyleSheet(
            "QListView::item:selected:active {background-color:#5A5A5A;} QListView::item:selected:!active {background-color:#5A5A5A;} QListView::item:hover:!selected {background-color:#121212;}")

    def add_track(self, playlistTrack):
        self.totalRuntime += playlistTrack.track.runtime
        item = PlaylistItemWidget(playlistTrack)
        item.playTrack.connect(lambda trackUri: self.playTrack.emit(self.playlist.playlistUri, trackUri))
        myQListWidgetItem = QListWidgetItem(self.trackList)
        myQListWidgetItem.setSizeHint(item.sizeHint())
        self.trackList.addItem(myQListWidgetItem)
        self.trackList.setItemWidget(myQListWidgetItem, item)
        self.infoLabel.setText(
            f"{self.playlist.ownerName} ▴ {len(self.trackList)} tracks ▴ {int(self.totalRuntime / 3600000)}h {int(self.totalRuntime / 60000 - 60 * int(self.totalRuntime / 3600000))}m")

    def list_selection_changed(self):
        selectedWidgets = set([self.trackList.itemWidget(item) for item in self.trackList.selectedItems()])
        newSelection = selectedWidgets - self.previousSelection
        deselected = self.previousSelection - selectedWidgets

        self.previousSelection = selectedWidgets

        for widget in newSelection:
            widget.selected()
        for widget in deselected:
            widget.deselected()
