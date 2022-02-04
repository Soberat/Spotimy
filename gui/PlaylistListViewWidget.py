import copy
import webbrowser
from typing import Union
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QMenu, QAction, \
    QFrame, QListView

from Spotify import Playlist, User
from gui.LabeledIconButton import LabeledIconButton
from gui.PlaylistListItemWidget import PlaylistListItemWidget
import resources


class PlaylistListWidget(QListWidget):

    deletePlaylist = pyqtSignal(Playlist)
    listChanged = pyqtSignal(list)
    playPlaylist = pyqtSignal(Playlist)

    # Reordering playlist is per session, it cannot be reflected in Spotify using API
    def __init__(self):
        super().__init__()
        self.playlists = list()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        drag = QDrag(self)
        indexes = self.selectedIndexes()
        drag.setMimeData(self.model().mimeData(indexes))
        drag.exec(supportedActions)

    def open_menu(self, point: QPoint):
        menu = QMenu()

        openInSpotify = QAction("Open in Spotify", self)
        openInSpotify.triggered.connect(self.open_playlist)

        unfollowPlaylist = QAction("Delete playlist", self)
        unfollowPlaylist.triggered.connect(self.delete_playlist)

        menu.addAction(openInSpotify)
        menu.addAction(unfollowPlaylist)

        menu.exec_(self.mapToGlobal(point))

    def open_playlist(self):
        if len(self.selectedItems()) != 0:
            webbrowser.open(self.itemWidget(self.selectedItems()[0]).playlist.playlistUri)

    def delete_playlist(self):
        if len(self.selectedItems()) != 0:
            playlistToDelete = self.itemWidget(self.selectedItems()[0]).playlist
            self.deletePlaylist.emit(playlistToDelete)
            self.takeItem(self.selectedIndexes()[0].row())
            self.playlists.remove(playlistToDelete)
            self.listChanged.emit(self.playlists)

    def add_item(self, playlist: Playlist, idx=None):
        itemWidget = PlaylistListItemWidget(playlist)
        itemWidget.playPlaylist.connect(self.playPlaylist.emit)
        if idx is not None:
            qListWidgetItem = QListWidgetItem()
            self.insertItem(idx, qListWidgetItem)
        else:
            qListWidgetItem = QListWidgetItem(self)
            self.addItem(qListWidgetItem)
        qListWidgetItem.setSizeHint(itemWidget.sizeHint())
        self.setItemWidget(qListWidgetItem, itemWidget)
        self.playlists.append(playlist)
        self.listChanged.emit(self.playlists)
        return playlist


class PlaylistListViewWidget(QWidget):

    COLUMN_WIDTH = 250
    selectionChanged = pyqtSignal(Playlist)
    openLiked = pyqtSignal(Playlist)
    playPlaylist = pyqtSignal(Playlist)
    newPlaylist = pyqtSignal()

    dummyPlaylist = Playlist({'images': list(),
                              'id': '',
                              'name': "No playlist!",
                              'snapshot_id': '',
                              'uri': ''}, User({'display_name': '', 'images': [{'url': None}], 'uri': None, 'id': ''}))

    def __init__(self):
        super().__init__()
        # Definitions of UI elements and their configuration
        self.previousSelection = None
        self.playlistList = PlaylistListWidget()

        self.playlistList.setFixedWidth(self.COLUMN_WIDTH)
        self.playlistList.itemSelectionChanged.connect(self.selection_changed)
        self.playlistList.playPlaylist.connect(self.playPlaylist.emit)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

        self.newPlaylistButton = LabeledIconButton("New playlist", ":/playlist_new.png")
        self.newPlaylistButton.clicked.connect(self.new_playlist)
        self.newPlaylistButton.setFixedWidth(self.COLUMN_WIDTH)
        layout.addWidget(self.newPlaylistButton, alignment=Qt.AlignLeft)

        self.likedSongsButton = LabeledIconButton("Liked songs", ":/playlist_liked.png")
        self.likedSongsButton.clicked.connect(self.open_liked)
        self.likedSongsButton.setFixedWidth(self.COLUMN_WIDTH)
        layout.addWidget(self.likedSongsButton, alignment=Qt.AlignLeft)

        frame = QFrame()
        frame.setStyleSheet("background-color: #282828;")
        frame.setFrameShape(QFrame.HLine)
        layout.addWidget(frame)
        layout.addWidget(self.playlistList)

    def selection_changed(self):
        try:
            selection = self.playlistList.itemWidget(self.playlistList.selectedItems()[0])
        except IndexError:
            # No item was selected
            self.selectionChanged.emit(self.dummyPlaylist)
            if self.previousSelection is not None:
                self.previousSelection.deselected()
            return

        if self.previousSelection is not None:
            try:
                self.previousSelection.deselected()
            except RuntimeError:
                pass
        selection.selected()
        self.previousSelection = selection
        self.selectionChanged.emit(selection.playlist)

    def new_playlist(self):
        self.newPlaylist.emit()

    def open_liked(self):
        self.playlistList.itemSelectionChanged.disconnect(self.selection_changed)
        if self.previousSelection is not None:
            try:
                self.previousSelection.deselected()
            except RuntimeError:
                pass
        playlist = copy.copy(self.dummyPlaylist)
        playlist.image = ":/playlist_liked.png"
        playlist.name = "Liked songs"
        self.openLiked.emit(playlist)
        self.playlistList.itemSelectionChanged.connect(self.selection_changed)