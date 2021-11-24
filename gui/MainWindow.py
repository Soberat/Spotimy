import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout
from PlaylistListViewWidget import PlaylistListViewWidget
from Spotify import Spotify, Playlist
from gui.PlaybackToolbar import PlaybackToolbar
from gui.PlaylistViewWidget import PlaylistViewWidget
import resources

# References:
# https://www.flaticon.com/free-icon/playlist_565266?term=playlist&page=1&position=5&page=1&position=5&related_id=565266&origin=search
# https://www.flaticon.com/premium-icon/musical-note_461146?term=note&page=1&position=12&page=1&position=12&related_id=461146&origin=search
# https://www.flaticon.com/free-icon/musical-note_898945?term=note&page=1&position=69&page=1&position=69&related_id=898945&origin=search
# https://www.flaticon.com/premium-icon/love_2901197?term=heart&page=1&position=24&page=1&position=24&related_id=2901197&origin=search

# TODO: Clearing old playlist cache
# pyrcc5 -o resources.py res/resources.qrc

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("* {background-color:#121212;} QLabel {color:#A8A8A8;} QListView::item:selected {background-color: #121212;} QListView::item:hover:!selected {background-color:#121212;} QScrollBar {border: 0px solid #121212;} QScrollBar::handle {background-color: #4d4d4d; width: 10px; border-radius: 0px} QScrollBar::up-arrow {background-color: #121212} QScrollBar::down-arrow {background-color: #121212} QScrollBar::left-arrow {background-color: #121212} QScrollBar::right-arrow {background-color: #121212} QListWidget {border: 2px solid #121212;border-radius: 4px;padding: 2px;} QSlider::sub-page:horizontal {background: #1db954; height: 40px;} QSlider::handle:horizontal {image: url(:/slider_handle.png);margin: -3px 0;} QSlider::groove:horizontal {background-color: #353535; border-radius: 2px}")
        # self.setStyleSheet("QWidget {border: 2px dot-dash green;border-radius: 4px;padding: 2px;}")

        self.centralWidgetLayout = QGridLayout()

        self.spotify = Spotify()
        self.trackGenerator = None
        self.playlistViews = dict()
        self.playlistGenerators = dict()
        self.trackTimer = None

        self.playlistListView = PlaylistListViewWidget()
        for playlist in self.spotify.get_user_playlists():
            self.playlistListView.add_item(playlist)
        self.playlistListView.selectionChanged.connect(self.change_playlist)

        self.playlistView = PlaylistViewWidget(PlaylistListViewWidget.dummyPlaylist)

        self.setCentralWidget(self.create_central_widget())

        playbackToolbar = PlaybackToolbar()
        playbackToolbar.widget.nextTrack.connect(lambda: self.spotify.sp.next_track(self.spotify.currentDevice))

        self.addToolBar(Qt.BottomToolBarArea, playbackToolbar)
        self.setMinimumSize(1400, 800)

    def create_central_widget(self):
        centralWidget = QWidget()
        centralWidget.setLayout(self.centralWidgetLayout)

        self.centralWidgetLayout.addWidget(self.playlistListView, 0, 0)
        self.centralWidgetLayout.addWidget(self.playlistView, 0, 1)
        self.centralWidgetLayout.setColumnStretch(1, 100)
        return centralWidget

    def change_playlist(self, playlist: Playlist):
        if playlist.name == PlaylistListViewWidget.dummyPlaylist.name:
            self.playlistView.setParent(None)
            if self.trackTimer is not None:
                self.trackTimer.stop()
            self.playlistView = PlaylistViewWidget(PlaylistListViewWidget.dummyPlaylist)
            self.playlistView.setParent(self)
            self.centralWidgetLayout.addWidget(self.playlistView, 0, 1)
            return
        if playlist.name not in self.playlistViews.keys():
            self.playlistViews[playlist.name] = (PlaylistViewWidget(playlist), self.spotify.get_playlist_tracks(playlist))

        try:
            self.playlistView.trackList.orderChanged.disconnect(self.update_order)
            self.playlistView.playTrack.disconnect(self.play_track)
        except TypeError:
            pass
        self.playlistView.setParent(None)
        self.playlistView, self.trackGenerator = self.playlistViews[playlist.name]
        self.playlistView.setParent(self)
        self.playlistView.trackList.orderChanged.connect(self.update_order)
        self.playlistView.playTrack.connect(self.play_track)
        self.centralWidgetLayout.addWidget(self.playlistView, 0, 1)

        self.trackTimer = QTimer().singleShot(0, self.populate_playlist_view)

    def populate_playlist_view(self):
        try:
            track = next(self.trackGenerator)
        except StopIteration:
            return
        except TypeError:
            self.trackTimer = QTimer().singleShot(0, self.populate_playlist_view)
            return

        self.playlistView.add_track(track)
        self.trackTimer = QTimer().singleShot(0, self.populate_playlist_view)

    def update_order(self, x, y):
        self.spotify.reorder_playlist(self.playlistView.playlist.id, x, y)

    def play_track(self, context, track):
        self.spotify.play_playlist(context, track)


app = QApplication(sys.argv)

try:
    import qdarkstyle

    app.setStyleSheet(qdarkstyle.load_stylesheet())
except ImportError as e:
    pass
# Create the parent Widget of the Widgets added to the layout
window = MainWindow()

# Show the parent Widget
window.show()

# Launch the application
sys.exit(app.exec())
