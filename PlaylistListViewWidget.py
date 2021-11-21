import webbrowser
from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent
from PyQt5.QtGui import QDrag, QMouseEvent, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QMenu, QAction, \
    QSplitter, QLabel, QHBoxLayout, QFrame

from Spotify import Playlist
from gui.PlaylistListItemWidget import PlaylistListItemWidget
import resources

# TODO: Add "New playlist" button
# TODO: Add "Liked songs" 'playlist'

class NewPlaylistPushButton(QFrame):

    clicked = pyqtSignal()

    def __init__(self, text):
        super().__init__()
        self.setStyleSheet("*:hover {background: gray}")
        self.iconLabel = QLabel()
        self.iconLabel.setPixmap(QPixmap(':/add_playlist.png').scaled(24, 24, transformMode=Qt.SmoothTransformation))

        self.textLabel = QLabel(text)
        font = self.textLabel.font()
        font.setPointSize(14)
        self.textLabel.setFont(font)

        layout = QHBoxLayout()
        layout.addWidget(self.iconLabel)
        layout.addWidget(self.textLabel, alignment=Qt.AlignVCenter)

        self.setLayout(layout)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()


class PlaylistListWidget(QListWidget):
    # Reordering playlist is per session, it cannot be reflected in Spotify using API
    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            "QListView::item:selected:!active {background-color:#346792;} QListView::item:hover:!selected {background-color:#19232d;}")

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        drag = QDrag(self)
        indexes = self.selectedIndexes()
        drag.setMimeData(self.model().mimeData(indexes))
        drag.exec(supportedActions)

    def open_menu(self, point: QPoint):
        menu = QMenu()

        openInSpotify = QAction("Open in Spotify", self)
        openInSpotify.triggered.connect(self.open_playlist)

        menu.addAction(openInSpotify)

        menu.exec_(self.mapToGlobal(point))

    def open_playlist(self):
        if len(self.selectedItems()) != 0:
            webbrowser.open(self.itemWidget(self.selectedItems()[0]).playlist.playlistUri)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            # self.selectionModel().select(self.indexAt(e.pos()), QItemSelectionModel.SelectionFlag.Select)
            return
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            # self.selectionModel().select(self.indexAt(e.pos()), QItemSelectionModel.SelectionFlag.Select)
            return
        super().mouseReleaseEvent(e)


class PlaylistListViewWidget(QWidget):
    selectionChanged = pyqtSignal(Playlist)

    dummyPlaylist = Playlist({'images': list(),
                              'id': '',
                              'name': "No playlist!",
                              'owner': {'display_name': ''},
                              'ownerPicture': None,
                              'snapshot_id': '',
                              'uri': ''})

    def __init__(self):
        super().__init__()
        # Definitions of UI elements and their configuration
        self.previousSelection = None
        self.playlistList = PlaylistListWidget()

        self.playlistList.setMaximumWidth(250)
        self.playlistList.itemSelectionChanged.connect(self.selection_changed)
        layout = QVBoxLayout()
        self.setLayout(layout)

        button = NewPlaylistPushButton("New playlist")
        button.clicked.connect(lambda: print("New playlist not implemented!"))

        layout.addWidget(button, alignment=Qt.AlignLeft)
        layout.addWidget(QSplitter())
        layout.addWidget(self.playlistList)

    def add_item(self, playlist: Playlist):
        item = PlaylistListItemWidget(playlist)
        qListWidgetItem = QListWidgetItem(self.playlistList)
        qListWidgetItem.setSizeHint(item.sizeHint())
        self.playlistList.addItem(qListWidgetItem)
        self.playlistList.setItemWidget(qListWidgetItem, item)

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
            self.previousSelection.deselected()
        selection.selected()
        self.previousSelection = selection
        self.selectionChanged.emit(selection.playlist)
