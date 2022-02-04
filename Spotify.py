import datetime
import json
import os
import time

import spotipy
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from spotipy import SpotifyOAuth, SpotifyException
from Secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI


# TODO: Store snapshot returned by reordering tracks

class PlaybackState:
    def __init__(self, shuffle=None, playing=None, loop=None, position=None):
        self.shuffle = shuffle
        self.playing = playing
        self.loop = loop
        self.position = position


class User:
    def __init__(self, userData):
        self.json = userData
        self.name = userData['display_name']
        try:
            self.image = userData['images'][0]['url']
        except IndexError:
            self.image = None
        self.id = userData['id']
        self.uri = userData['uri']


class Device:
    def __init__(self, deviceData):
        self.id = deviceData['id']
        self.isActive = deviceData['is_active']
        self.isPrivateSession = deviceData['is_private_session']
        self.isRestricted = deviceData['is_restricted']
        self.name = deviceData['name']
        self.type = deviceData['type']
        self.volume = deviceData['volume_percent']

    def __cmp__(self, other):
        return self.id > other.id


class Playlist:
    def __init__(self, playlistData: dict, owner: User):
        try:
            self.image = playlistData['images'][0]['url']
        except IndexError:
            self.image = None
        self.id = playlistData['id']
        self.name = playlistData['name']
        self.owner = owner
        self.snapshotId = playlistData['snapshot_id']
        self.playlistUri = playlistData['uri']


class Track:
    def __init__(self, trackData: dict):
        if trackData is None:
            return
        try:
            self.albumCoverUri: str = trackData['album']['images'][-1]['url']
        except IndexError:
            self.albumCoverUri = None
        self.title = trackData['name']
        self.artists = [artist['name'] for artist in trackData['artists']]
        self.artistUris = [artist['uri'] for artist in trackData['artists']]
        self.album = trackData['album']['name']
        self.runtime: int = trackData['duration_ms']
        self.trackUri = trackData['uri']
        try:
            self.year = trackData['album']['release_date'].split(sep="-")[0]
        except AttributeError:
            self.year = datetime.datetime.year


class PlaylistTrack:
    def __init__(self, playlistTrackData, index):
        self.index = index
        self.addedAt = playlistTrackData['added_at']
        # self.addedBy = playlistTrackData['added_by']
        self.isLocal = playlistTrackData['is_local']
        # self.primaryColor = playlistTrackData['primary_color']
        # self.videoThumbnail = playlistTrackData['video_thumbnail']
        self.track = Track(playlistTrackData['track'])


def ThrowsSpotifyException(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except SpotifyException as se:
            print(se.reason)
            return False

    return wrapper


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
        self.deviceList = None
        self.__userPlaylistsFullDict = None
        self.currentDevice = None

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(scope=' '.join(self.scope), client_id=SPOTIPY_CLIENT_ID,
                                      client_secret=SPOTIPY_CLIENT_SECRET,
                                      redirect_uri=SPOTIPY_REDIRECT_URI))

        self.user = User(self.sp.current_user())

    # TODO: Cache
    def get_user_playlists(self):
        # Use cached result if possible
        if self.__userPlaylistsFullDict is None:
            self.__userPlaylistsFullDict = self.sp.current_user_playlists()['items']
        for playlist in self.__userPlaylistsFullDict:
            yield Playlist(playlistData=playlist, owner=User(self.sp.user(playlist['owner']['id'])))

    def get_saved_tracks(self):
        # Saved tracks are not cached, since they don't have a snapshot ID
        liked = self.sp.current_user_saved_tracks()

        i = 0
        # We have enough information to <just> not require a new class just for liked tracks
        for track in liked['items']:
            i += 1
            track['is_local'] = False  # You can't like local tracks
            yield PlaylistTrack(track, i)

        while liked['next']:
            for track in liked['items']:
                i += 1
                track['is_local'] = False  # You can't like local tracks
                yield PlaylistTrack(track, i)

    def get_playlist_tracks(self, playlist: Playlist):
        if not os.path.exists("./cache/playlists"):
            os.makedirs("./cache/playlists")
        if playlist.snapshotId in os.listdir("./cache/playlists"):
            with open(f'./cache/playlists/{playlist.snapshotId}', 'r') as snapshotFile:
                snapshot = json.load(snapshotFile)
                i = 0
                for track in snapshot['tracks']:
                    i += 1
                    yield PlaylistTrack(track, i)
        else:
            snapshot = dict()
            snapshot['image'] = playlist.image
            snapshot['id'] = playlist.id
            snapshot['name'] = playlist.name
            snapshot['owner'] = playlist.owner.json
            snapshot['snapshot_id'] = playlist.snapshotId
            snapshot['tracks'] = []

            tracks = self.sp.playlist(playlist.id, fields="tracks,next")['tracks']
            i = 0
            for track in tracks['items']:
                i += 1
                snapshot['tracks'].append(track)
                yield PlaylistTrack(track, i)

            while tracks['next']:
                tracks = self.sp.next(tracks)
                for track in tracks['items']:
                    # Some playlist items might not have the track property
                    if track['track'] is None:
                        continue
                    i += 1
                    snapshot['tracks'].append(track)
                    yield PlaylistTrack(track, i)

            with open(f'./cache/playlists/{playlist.snapshotId}', 'w') as snapshotFile:
                json.dump(snapshot, snapshotFile)

    def get_current_playback(self):
        playback = self.sp.current_playback()
        if playback is not None and playback['device']['is_private_session']:
            return None, Device(playback['device']), None

        if playback is not None:
            self.currentDevice = Device(playback['device'])
            return Track(playback['item']), self.currentDevice, PlaybackState(shuffle=playback['shuffle_state'],
                                                                              playing=playback['is_playing'],
                                                                              loop=playback['repeat_state'],
                                                                              position=playback['progress_ms'])
        else:
            return None, None, None

    def get_devices(self):
        for deviceData in self.sp.devices()['devices']:
            yield Device(deviceData)

    def __update_devices(self):
        devices = self.sp.devices()['devices']
        newDeviceList = set()
        for deviceData in devices:
            newDeviceList.add(Device(deviceData))
            device = Device(deviceData)
            if device.isActive:
                self.currentDevice = device

        newDeviceList = sorted(newDeviceList)

        if newDeviceList != self.deviceList:
            self.deviceList = newDeviceList

    @ThrowsSpotifyException
    def get_active_device(self):
        self.__update_devices()
        return self.currentDevice

    @ThrowsSpotifyException
    def get_current_user(self):
        return self.user

    @ThrowsSpotifyException
    def set_shuffle(self, state: bool):
        self.__update_devices()
        self.sp.shuffle(state)

    @ThrowsSpotifyException
    def previous_track(self):
        self.__update_devices()
        self.sp.previous_track()

    @ThrowsSpotifyException
    def play_pause(self, play: bool):
        try:
            if play:
                self.sp.start_playback()
            else:
                self.sp.pause_playback()
        except SpotifyException:
            pass

    @ThrowsSpotifyException
    def next_track(self):
        self.sp.next_track()

    @ThrowsSpotifyException
    def next_repeat_mode(self):
        self.sp.repeat()

    @ThrowsSpotifyException
    def set_volume(self, value):
        self.sp.volume(value)

    @ThrowsSpotifyException
    def play_track(self, context, targetUri):
        if "spotify:local" not in targetUri:
            if context == '':
                self.sp.start_playback(uris=[targetUri])
            else:
                self.sp.start_playback(context_uri=context, offset={"uri": targetUri})

    @ThrowsSpotifyException
    def reorder_playlist(self, playlistId, rangeStart, insertBefore, snapshotId=None):
        newSnapshotId = self.sp.playlist_reorder_items(playlist_id=playlistId, range_start=rangeStart,
                                                       insert_before=insertBefore, snapshot_id=snapshotId)
        return newSnapshotId

    @ThrowsSpotifyException
    def add_to_playlist(self, playlist: Playlist, tracks: list):
        self.sp.playlist_add_items(playlist.id, [track.trackUri for track in tracks])
        return True

    @ThrowsSpotifyException
    def remove_from_playlist(self, playlist: Playlist, tracks: list):
        self.sp.playlist_remove_specific_occurrences_of_items(playlist.id, [{"uri": playlistTrack.track.trackUri, "positions": [playlistTrack.index-1]} for playlistTrack in tracks])

    @ThrowsSpotifyException
    def add_new_playlist(self):
        return Playlist(self.sp.user_playlist_create(self.user.id, "New playlist"), self.user)

    @ThrowsSpotifyException
    def unfollow_playlist(self, user: User, playlist: Playlist):
        self.sp.user_playlist_unfollow(user.id, playlist.id)


class WorkerSignals(QObject):
    stateReady = pyqtSignal(tuple)


class Worker(QRunnable, QObject):
    def __init__(self, spotify: Spotify):
        super().__init__()
        self.spotify = spotify
        self.signals = WorkerSignals()

    def run(self):
        while True:
            self.signals.stateReady.emit(self.spotify.get_current_playback())
            time.sleep(1)
