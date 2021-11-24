import json
import os

import spotipy
from spotipy import SpotifyOAuth
from Secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

# TODO: Store snapshot returned by reordering tracks


class Device:
    def __init__(self, deviceData):
        self.id = deviceData['id']
        self.isActive = deviceData['is_active']
        self.isPrivateSession = deviceData['is_private_session']
        self.isRestricted = deviceData['is_restricted']
        self.name = deviceData['name']
        self.type = deviceData['type']
        self.volume = deviceData['volume_percent']


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
        self.playlistUri = playlistData['uri']


class Track:
    def __init__(self, trackData: dict):
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


class PlaylistTrack:
    def __init__(self, playlistTrackData, index):
        self.index = index
        self.addedAt = playlistTrackData['added_at']
        # self.addedBy = playlistTrackData['added_by']
        self.isLocal = playlistTrackData['is_local']
        # self.primaryColor = playlistTrackData['primary_color']
        # self.videoThumbnail = playlistTrackData['video_thumbnail']
        self.track = Track(playlistTrackData['track'])


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
        self.currentDevice = None

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
            snapshot['ownerName'] = playlist.ownerName
            snapshot['ownerPicture'] = playlist.ownerPicture
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

    def get_active_device(self):
        self.__update_devices()
        return self.currentDevice

    def set_shuffle(self, state: bool):
        self.__update_devices()
        self.sp.shuffle(state)

    def previous_track(self):
        self.__update_devices()
        self.sp.previous_track()

    def play_pause(self, play: bool):
        try:
            if play:
                self.sp.start_playback()
            else:
                self.sp.pause_playback()
        except SpotifyException:
            pass

    def next_track(self):
        self.__update_devices()
        self.sp.next_track()

    def next_repeat_mode(self):
        self.sp.repeat()

    def set_volume(self, value):
        self.sp.volume(value)

    def play_track(self, context, targetUri):
        if "spotify:local" not in targetUri:
            self.sp.start_playback(context_uri=context, offset={"uri": targetUri})

    def reorder_playlist(self, playlistId, rangeStart, insertBefore, snapshotId=None):
        newSnapshotId = self.sp.playlist_reorder_items(playlist_id=playlistId, range_start=rangeStart,
                                                       insert_before=insertBefore, snapshot_id=snapshotId)
