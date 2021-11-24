# Widget presenting the playlist in a similar way Spotify does
from typing import Union

from PyQt5.QtCore import Qt, QModelIndex, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QImage, QBitmap, QDrag
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView, \
    QMenu, QAction, QActionGroup, QSplitter

import CachingImageGetter
from CachingImageGetter import get_image
from Spotify import Playlist
from gui.PlaylistItemWidget import PlaylistItemWidget
import webbrowser


# TODO: Add "Move to index" context menu option
# TODO: Split header info string into multiple labels
# TODO: Add gradient as background


class TrackListWidget(QListWidget):

    orderChanged = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        self.model().rowsMoved.connect(self.update_indexes)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        drag = QDrag(self)
        indexes = self.selectedIndexes()
        drag.setMimeData(self.model().mimeData(indexes))
        drag.exec(supportedActions)

    def open_menu(self, point: QPoint):
        menu = QMenu()

        moveToTop = QAction("Move to top", self)
        moveToBottom = QAction("Move to bottom", self)
        moveToTop.triggered.connect(self.move_to_top)
        moveToBottom.triggered.connect(self.move_to_bottom)

        menu.addAction(moveToTop)
        menu.addAction(moveToBottom)

        # If a single song was selected, add more options
        if len(self.selectedIndexes()) == 1:
            track = self.itemWidget(self.selectedItems()[0]).track
            menu.addSeparator()
            openInSpotify = QAction("Open in Spotify", self)
            openInSpotify.triggered.connect(
                lambda: webbrowser.open(track.trackUri))
            menu.addAction(openInSpotify)

            if len(track.artists) == 1:
                action = QAction("Open artist page")
                action.triggered.connect(lambda: webbrowser.open(track.artistUris[0]))
                menu.addAction(action)
            else:
                artistsMenu = QMenu("Open artist's page")
                actionGroup = QActionGroup(artistsMenu)
                for idx, artist in enumerate(self.itemWidget(self.selectedItems()[0]).track.artists):
                    actionGroup.addAction(artistsMenu.addAction(artist)).setData(idx)

                actionGroup.triggered.connect(lambda data: webbrowser.open(track.artistUris[data.data()]))
                menu.addMenu(artistsMenu)

        menu.exec_(self.mapToGlobal(point))

    def move_to_top(self):
        selection = sorted(self.selectedIndexes(), reverse=True)
        # We can't iterate over the indexes, since they can change after moving rows
        for idx in range(len(selection)):
            if selection[0].row() == 0:
                return
            self.model().beginMoveRows(self.rootIndex(), selection[0].row(), selection[0].row(), self.rootIndex(), 0)
            self.model().endMoveRows()
            selection = sorted(self.selectedIndexes(), reverse=True)

    def move_to_bottom(self):
        bottomIdx = len(self)
        selection = sorted(self.selectedIndexes())
        # We can't iterate over the indexes, since they can change after moving rows
        for idx in range(len(selection)):
            if selection[0].row() == bottomIdx - idx:
                return
            self.model().beginMoveRows(self.rootIndex(), selection[0].row(), selection[0].row(), self.rootIndex(), bottomIdx)
            self.model().endMoveRows()
            selection = sorted(self.selectedIndexes())
        self.scrollToBottom()

    def update_indexes(self, idx1: QModelIndex, start, stop, idx2: QModelIndex, row):
        self.orderChanged.emit(start, row)
        widgets = []
        for idx in range(len(self)):
            widgets.append(self.itemWidget(self.item(idx)))
        for idx, widget in enumerate(widgets):
            widget.indexLabel.setText(str(idx + 1))
        self.scrollToTop()


class PlaylistViewWidget(QWidget):

    playTrack = pyqtSignal(str, str)

    def __init__(self, playlist: Playlist):
        super().__init__()
        self.playlist = playlist
        self.totalRuntime = 0
        self.previousSelection = set()

        self.setStyleSheet("QSplitter::handle {width: 10px; height: 10px; background-color: green; color: #ff00aa; border: 40px solid green; border-radius: 4px;}")

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
