import webbrowser
from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QModelIndex
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QMenu, QAction, QActionGroup, QListWidgetItem

from Spotify import Playlist


class TrackListWidget(QListWidget):

    orderChanged = pyqtSignal(int, int)
    addToPlaylist = pyqtSignal(Playlist, list)

    def __init__(self):
        super().__init__()

        self.playlistList = []

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
        addToPlaylistMenu = QMenu("Add to playlist")
        playlistsActionGroup = QActionGroup(addToPlaylistMenu)

        for idx, playlist in enumerate(self.playlistList):
            playlistsActionGroup.addAction(addToPlaylistMenu.addAction(playlist.name)).setData(idx)

        playlistsActionGroup.triggered.connect(self.add_to_playlist)

        moveToTop.triggered.connect(self.move_to_top)
        moveToBottom.triggered.connect(self.move_to_bottom)

        menu.addAction(moveToTop)
        menu.addAction(moveToBottom)
        menu.addMenu(addToPlaylistMenu)

        # If a single song was selected, add more options
        if len(self.selectedIndexes()) == 1:
            track = self.itemWidget(self.selectedItems()[0]).playlistTrack.track
            menu.addSeparator()
            openInSpotify = QAction("Open in Spotify", self)
            openInSpotify.triggered.connect(
                lambda: webbrowser.open(track.trackUri))
            menu.addAction(openInSpotify)

            moveAlphabetical = QAction("Move up until sorted", self)
            moveAlphabetical.triggered.connect(self.move_alphabetical)
            menu.addAction(moveAlphabetical)

            if len(track.artists) == 1:
                action = QAction("Open artist page")
                action.triggered.connect(lambda: webbrowser.open(track.artistUris[0]))
                menu.addAction(action)
            else:
                artistsMenu = QMenu("Open artist's page")
                actionGroup = QActionGroup(artistsMenu)
                for idx, artist in enumerate(track.artists):
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

    def move_alphabetical(self):
        selection = sorted(self.selectedIndexes())[0]
        searchIndex = 1
        artist = self.indexWidget(selection).playlistTrack.track.artists[0]
        nextArtist = self.indexWidget(selection.siblingAtRow(selection.row() - searchIndex)).playlistTrack.track.artists[0]
        while artist < nextArtist:
            searchIndex += 1
            nextArtist = self.indexWidget(selection.siblingAtRow(selection.row() - searchIndex)).playlistTrack.track.artists[0]

        self.model().beginMoveRows(self.rootIndex(), selection.row(), selection.row(), self.rootIndex(), selection.row() - searchIndex + 1)
        self.model().endMoveRows()
        self.scrollTo(selection.siblingAtRow(selection.row() - searchIndex + 1))

    def add_to_playlist(self, playlistIndex):
        selection = self.selectedItems()
        tracks = []
        for item in selection:
            track = self.itemWidget(item).playlistTrack
            if not track.isLocal:
                tracks.append(track.track)

        self.addToPlaylist.emit(self.playlistList[playlistIndex.data()], tracks)

    def update_indexes(self, idx1: QModelIndex, start, stop, idx2: QModelIndex, row):
        self.orderChanged.emit(start, row)
        widgets = []
        for idx in range(len(self)):
            widgets.append(self.itemWidget(self.item(idx)))
        for idx, widget in enumerate(widgets):
            widget.indexLabel.setText(str(idx + 1))
        self.scrollToTop()

    def add_widget(self, itemWidget):
        myQListWidgetItem = QListWidgetItem(self)
        myQListWidgetItem.setSizeHint(itemWidget.sizeHint())
        self.addItem(myQListWidgetItem)
        self.setItemWidget(myQListWidgetItem, itemWidget)

    def update_playlist_list(self, playlistList):
        self.playlistList = playlistList
