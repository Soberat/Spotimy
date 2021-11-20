from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QListWidget, QListWidgetItem

from Spotify import Playlist
from gui.PlaylistListItemWidget import PlaylistListItemWidget


# TODO: Disallow new selection while dragging

class PlaylistListViewWidget(QWidget):
    selectionChanged = pyqtSignal(Playlist)

    dummyPlaylist = Playlist({'images': list(),
                              'id': '',
                              'name': "No playlist!",
                              'owner': {'display_name': ''},
                              'snapshot_id': ''})

    def __init__(self):
        super().__init__()
        # Definitions of UI elements and their configuration
        self.previousSelection = None
        self.playlistList = QListWidget(self)
        self.playlistList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlistList.setStyleSheet(
            "QListView::item:selected:!active {background-color:#346792;} QListView::item:hover:!selected {background-color:#19232d;}")

        self.playlistList.setMaximumWidth(250)
        self.playlistList.itemSelectionChanged.connect(self.selection_changed)
        layout = QVBoxLayout()
        self.setLayout(layout)
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
