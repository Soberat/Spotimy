import json
import os

import spotipy
from spotipy import SpotifyOAuth
from Secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI


class Playlist:
    def __init__(self, playlistData: dict):
        try:
            self.image = playlistData['images'][0]['url']
        except IndexError:
            self.image = None
        self.id = playlistData['id']
        self.name = playlistData['name']
        self.ownerName = playlistData['owner']['display_name']
        self.ownerPicture = playlistData['ownerPicture']
        self.snapshotId = playlistData['snapshot_id']


class Track:
    def __init__(self, idx, trackData: dict):
        self.index: int = idx
        try:
            self.albumCoverUri: str = trackData['track']['album']['images'][-1]['url']
        except IndexError:
            self.albumCoverUri = None
        self.title = trackData['track']['name']
        self.artists = [artist['name'] for artist in trackData['track']['artists']]
        self.album = trackData['track']['album']['name']
        self.added: str = trackData['added_at']
        self.runtime: int = trackData['track']['duration_ms']


class Spotify:
    scope = ["ugc-image-upload",
             "playlist-modify-private",
             "playlist-read-private",
             "playlist-modify-public",
             "playlist-read-collaborative",
             "user-read-private",
             "user-read-email",
             "user-read-playback-state",
             "user-modify-playback-state",
             "user-read-currently-playing",
             "user-library-modify",
             "user-library-read",
             "user-read-playback-position",
             "user-read-recently-played",
             "user-top-read",
             "app-remote-control",
             "streaming",
             "user-follow-modify",
             "user-follow-read"]

    def __init__(self):
        super().__init__()
        self.__userPlaylistsFullDict = None

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(scope=' '.join(self.scope), client_id=SPOTIPY_CLIENT_ID,
                                      client_secret=SPOTIPY_CLIENT_SECRET,
                                      redirect_uri=SPOTIPY_REDIRECT_URI))

    def get_user_playlists(self):
        # Use cached result if possible
        if self.__userPlaylistsFullDict is None:
            self.__userPlaylistsFullDict = self.sp.current_user_playlists()['items']
        for playlist in self.__userPlaylistsFullDict:
            playlist['ownerPicture'] = self.sp.user(playlist['owner']['id'])['images'][0]['url']
            yield Playlist(playlistData=playlist)

    def get_playlist_tracks(self, playlist: Playlist):
        if playlist.snapshotId in os.listdir("./cache/playlists"):
            with open(f'./cache/playlists/{playlist.snapshotId}', 'r') as snapshotFile:
                snapshot = json.load(snapshotFile)
                i = 0
                for track in snapshot['tracks']:
                    i += 1
                    yield Track(i, track)
        else:
            snapshot = dict()
            snapshot['image'] = playlist.image
            snapshot['id'] = playlist.id
            snapshot['name'] = playlist.name
            snapshot['ownerName'] = playlist.ownerName
            snapshot['ownerPicture'] = playlist.ownerPicture
            snapshot['snapshot_id'] = playlist.snapshotId
            snapshot['tracks'] = []

            tracks = self.sp.playlist(playlist.id, fields="tracks,next")['tracks']
            i = 0
            for track in tracks['items']:
                i += 1
                snapshot['tracks'].append(track)
                yield Track(i, track)

            while tracks['next']:
                tracks = self.sp.next(tracks)
                for track in tracks['items']:
                    i += 1
                    snapshot['tracks'].append(track)
                    yield Track(i, track)

            with open(f'./cache/playlists/{playlist.snapshotId}', 'w') as snapshotFile:
                json.dump(snapshot, snapshotFile)

    def reorder_playlist(self, playlistId, rangeStart, insertBefore, snapshotId=None):
        newSnapshotId = self.sp.playlist_reorder_items(playlist_id=playlistId, range_start=rangeStart, insert_before=insertBefore, snapshot_id=snapshotId)
