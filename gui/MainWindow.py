import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QLabel
from PlaylistListViewWidget import PlaylistListViewWidget
from Spotify import Spotify, Playlist
from gui.PlaylistViewWidget import PlaylistViewWidget


# TODO: Cache playlist data
# TODO: Download and cache playlist/track covers

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.centralWidgetLayout = QGridLayout()

        self.spotify = Spotify()
        self.trackGenerator = None

        self.playlistListView = PlaylistListViewWidget()
        for playlist in self.spotify.get_user_playlists():
            self.playlistListView.add_item(playlist)
        self.playlistListView.selectionChanged.connect(self.change_playlist)

        self.playlistView = QLabel("Empty lol")

        self.setCentralWidget(self.create_central_widget())

    def create_central_widget(self):
        centralWidget = QWidget()
        centralWidget.setLayout(self.centralWidgetLayout)

        self.centralWidgetLayout.addWidget(self.playlistListView, 0, 0)
        self.centralWidgetLayout.addWidget(self.playlistView, 0, 1)
        self.centralWidgetLayout.setColumnStretch(1, 100)
        return centralWidget

    def change_playlist(self, playlist: Playlist):
        self.centralWidgetLayout.removeWidget(self.playlistView)
        self.playlistView = PlaylistViewWidget(playlist)
        self.centralWidgetLayout.addWidget(self.playlistView, 0, 1)
        self.trackGenerator = self.spotify.get_playlist_tracks(playlist)

        QTimer().singleShot(0, self.populate_playlist_view)

    def populate_playlist_view(self):
        try:
            track = next(self.trackGenerator)
        except StopIteration:
            self.trackGenerator = None
            return
        except TypeError:
            return

        self.playlistView.add_track(track)
        QTimer().singleShot(0, self.populate_playlist_view)


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
