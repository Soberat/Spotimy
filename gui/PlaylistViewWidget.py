# Widget presenting the playlist in a similar way Spotify does
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QImage, QBitmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView

from CachingImageGetter import get_image
from Spotify import Playlist
from gui.PlaylistItemWidget import PlaylistItemWidget


class PlaylistViewWidget(QWidget):
    def __init__(self, playlist: Playlist):
        super().__init__()
        self.playlist = playlist
        self.totalRuntime = 0
        self.previousSelection = set()

        self.mainLayout = QVBoxLayout()

        self.coverLabel = QLabel()
        self.coverLabel.setPixmap(get_image(playlist.image).scaled(192, 192, transformMode=Qt.SmoothTransformation))

        # Font: Vision - Free Font Family
        self.nameLabel = QLabel(playlist.name)
        self.nameLabel.setFont(QFont('Gotham', 36, QFont.Black))

        self.ownerPictureLabel = QLabel()
        self.ownerPictureLabel.setFixedHeight(40)
        picture = QPixmap(playlist.ownerPicture).scaled(512, 512, transformMode=Qt.SmoothTransformation)
        mask = QImage('pfp_mask.png').createAlphaMask()
        picture.setMask(QBitmap.fromImage(mask))
        self.ownerPictureLabel.setPixmap(picture.scaled(30, 30, transformMode=Qt.SmoothTransformation))

        self.infoLabel = QLabel()
        self.infoLabel.setFont(QFont('Gotham', 12, QFont.Normal))
        self.infoLabel.setFixedHeight(40)

        self.trackList = QListWidget(self)
        self.trackList.setSelectionMode(QAbstractItemView.ExtendedSelection)

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
        self.mainLayout.addWidget(self.trackList)
        self.mainLayout.setStretch(1, 10)

        self.setLayout(self.mainLayout)
        self.setMinimumSize(500, 500)

        self.trackList.itemSelectionChanged.connect(self.list_selection_changed)
        self.trackList.setStyleSheet("QListView::item:selected:!active {background-color:#346792;} QListView::item:hover:!selected {background-color:#19232d;}")

    def add_track(self, track):
        self.totalRuntime += track.runtime
        item = PlaylistItemWidget(track)
        myQListWidgetItem = QListWidgetItem(self.trackList)
        myQListWidgetItem.setSizeHint(item.sizeHint())
        self.trackList.addItem(myQListWidgetItem)
        self.trackList.setItemWidget(myQListWidgetItem, item)
        self.infoLabel.setText(f"{self.playlist.ownerName} ▴ {len(self.trackList)} tracks ▴ {int(self.totalRuntime/3600000)}h {int(self.totalRuntime/60000 - 60*int(self.totalRuntime/3600000))}m")

    def list_selection_changed(self):
        selectedWidgets = set([self.trackList.itemWidget(item) for item in self.trackList.selectedItems()])
        newSelection = selectedWidgets - self.previousSelection
        deselected = self.previousSelection - selectedWidgets

        self.previousSelection = selectedWidgets

        for widget in newSelection:
            widget.selected()
        for widget in deselected:
            widget.deselected()
