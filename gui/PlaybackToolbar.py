from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent, QFont
from PyQt5.QtWidgets import QToolBar, QHBoxLayout, QPushButton, QWidget, QLabel, QVBoxLayout, QSlider

import CachingImageGetter
from Spotify import Track, PlaybackState


# TODO: Color buttons when hovered
# TODO: Color buttons based on state
# TODO: Resize play/pause button on hover
# TODO: Add functions to control states
# TODO: Change runtime to remaining time on click
# TODO: Disable external setting volume when volume handle is grabbed


class ToolbarButton(QWidget):

    clicked = pyqtSignal()

    def __init__(self, pixmapPath: str, sizeX, sizeY):
        super().__init__()

        self.x = sizeX
        self.y = sizeY

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()
        self.pixmap = QPixmap(pixmapPath).scaled(sizeX, sizeY, transformMode=Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)
        layout.addWidget(self.label)

    def change_pixmap(self, pixmapPath: str):
        self.pixmap = QPixmap(pixmapPath).scaled(self.x, self.y, transformMode=Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            pass
        elif event.type() == QEvent.HoverLeave:
            pass
        return super().event(event)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()


class PlaybackWidget(QWidget):

    shuffleChanged = pyqtSignal(bool)
    previousTrack = pyqtSignal()
    playPause = pyqtSignal(bool)
    nextTrack = pyqtSignal()
    loopChanged = pyqtSignal(bool)
    volumeChanged = pyqtSignal(int)

    iconSize = 12
    albumCoverSize = 80

    def __init__(self):
        super().__init__()

        self.track = None

        self.trackCoverLabel = QLabel()
        self.trackCoverLabel.setPixmap(QPixmap(':/track_placeholder.png').scaled(self.albumCoverSize, self.albumCoverSize, transformMode=Qt.SmoothTransformation))
        self.trackCoverLabel.setContentsMargins(-1, -1, -1, -1)
        self.trackCoverLabel.setMargin(0)
        # self.trackCoverLabel.setStyleSheet("padding: 0 0 0 0; border-spacing: 0px 0px 0px 0px; margin: 0px;")

        self.titleLabel = QLabel("I Know There's Gonna Be (Good Times)")
        self.titleLabel.setFont(QFont("Gotham Book", 9, QFont.Bold))
        self.titleLabel.setStyleSheet("color: #FFFFFF;")
        self.artistsLabel = QLabel("Young Thug, Jamie xx, Popcaan")
        self.artistsLabel.setFont(QFont("Gotham Book", 7, QFont.Bold))

        self.shuffleState = False
        self.shuffleButton = ToolbarButton(":/shuffle.png", self.iconSize, self.iconSize)
        self.shuffleButton.clicked.connect(self.shuffle_pushed)

        self.previousButton = ToolbarButton(":/previous.png", self.iconSize, self.iconSize)
        self.previousButton.clicked.connect(self.previousTrack.emit)

        self.playPauseButton = ToolbarButton(":/play.png", 32, 32)
        self.playPauseButton.clicked.connect(self.play_pause_pushed)
        self.statePlaying = False

        self.nextButton = ToolbarButton(":/next.png", self.iconSize, self.iconSize)
        self.nextButton.clicked.connect(self.nextTrack.emit)

        self.loopButton = ToolbarButton(":/loop.png", self.iconSize, self.iconSize)
        self.loopButton.clicked.connect(self.loopChanged.emit)

        self.timeLabel = QLabel("0:00")

        self.trackSlider = QSlider(Qt.Horizontal)
        self.trackSlider.setFixedWidth(700)

        self.runtimeLabel = QLabel("0:00")

        self.queueButton = ToolbarButton(":/queue.png", self.iconSize, self.iconSize)
        self.devicesButton = ToolbarButton(":/connect.png", self.iconSize, self.iconSize)

        self.previousVolume = 40

        self.volumeButton = ToolbarButton(":/sound_mute.png", self.iconSize, self.iconSize)
        self.volumeButton.clicked.connect(self.mute_pushed)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.valueChanged.connect(self.change_volume)
        self.volumeSlider.setFixedWidth(100)
        self.volumeSlider.setSingleStep(1)

        self.maximizeButton = ToolbarButton(":/maximize.png", self.iconSize, self.iconSize)

        layout = QHBoxLayout()

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.trackCoverLabel)

        innerLayout = QVBoxLayout()
        innerLayout.addStretch(100)
        innerLayout.addWidget(self.titleLabel)
        innerLayout.addWidget(self.artistsLabel)
        innerLayout.addStretch(100)

        layout.addLayout(innerLayout)

        controlLayout = QVBoxLayout()
        innerControlLayout = QHBoxLayout()

        innerControlLayout.addStretch(1000)
        innerControlLayout.addWidget(self.shuffleButton)
        innerControlLayout.addWidget(self.previousButton)
        innerControlLayout.addWidget(self.playPauseButton)
        innerControlLayout.addWidget(self.nextButton)
        innerControlLayout.addWidget(self.loopButton)
        innerControlLayout.addStretch(1000)

        sliderLayout = QHBoxLayout()

        sliderLayout.addStretch(1000)
        sliderLayout.addWidget(self.timeLabel)
        sliderLayout.addWidget(self.trackSlider)
        sliderLayout.addWidget(self.runtimeLabel)
        sliderLayout.addStretch(1000)

        controlLayout.addLayout(innerControlLayout)
        controlLayout.addLayout(sliderLayout)

        layout.addLayout(controlLayout)
        layout.setStretch(2, 100)

        rightCornerLayout = QHBoxLayout()

        rightCornerLayout.addWidget(self.queueButton)
        rightCornerLayout.addWidget(self.devicesButton)
        rightCornerLayout.addWidget(self.volumeButton)
        rightCornerLayout.addWidget(self.volumeSlider)
        rightCornerLayout.addWidget(self.maximizeButton)

        layout.addLayout(rightCornerLayout)

        self.setLayout(layout)
        self.setMinimumWidth(1000)

    def set_track(self, track: Track):
        self.track = track
        self.trackCoverLabel.setPixmap(CachingImageGetter.get_image(track.albumCoverUri).scaled(self.albumCoverSize, self.albumCoverSize, transformMode=Qt.SmoothTransformation))
        self.titleLabel.setText(track.title)
        self.artistsLabel.setText(", ".join(track.artists))
        time = track.runtime / 1000
        minutes = int(time / 60)
        seconds = int(time - 60 * minutes)
        self.runtimeLabel.setText(f"{minutes:02d}:{seconds:02d}")
        self.trackSlider.setRange(0, track.runtime)

        self.titleLabel.setFixedWidth(
            self.maximizeButton.width() + self.volumeSlider.width() + self.volumeButton.width() + self.devicesButton.width() + self.queueButton.width() - self.trackCoverLabel.width())
        self.artistsLabel.setFixedWidth(
            self.maximizeButton.width() + self.volumeSlider.width() + self.volumeButton.width() + self.devicesButton.width() + self.queueButton.width() - self.trackCoverLabel.width())

    def set_playback_state(self, playbackState: PlaybackState):
        # set shuffle
        # set playing
        time = playbackState.position / 1000
        minutes = int(time / 60)
        seconds = int(time - 60 * minutes)
        self.timeLabel.setText(f"{minutes:02d}:{seconds:02d}")
        self.trackSlider.setValue(playbackState.position)
        # set loop

    def set_volume(self, value):
        self.volumeSlider.setValue(value)

    def shuffle_pushed(self):
        self.shuffleState = not self.shuffleState
        self.shuffleChanged.emit(self.shuffleState)

    def play_pause_pushed(self):
        if not self.statePlaying:
            self.playPauseButton.change_pixmap(':/pause.png')
            self.statePlaying = True
        else:
            self.playPauseButton.change_pixmap(':/play.png')
            self.statePlaying = False
        self.playPause.emit(self.statePlaying)

    def mute_pushed(self):
        if self.volumeSlider.value() != 0:
            self.previousVolume = self.volumeSlider.value()
            self.volumeSlider.setValue(0)
        else:
            self.volumeSlider.setValue(self.previousVolume)

    def change_volume(self):
        value = self.volumeSlider.value()
        if value == 0:
            self.volumeButton.change_pixmap(":/sound_mute.png")
        elif value <= 30:
            self.volumeButton.change_pixmap(":/sound_quiet.png")
        elif value <= 70:
            self.volumeButton.change_pixmap(":/sound_normal.png")
        else:
            self.volumeButton.change_pixmap(":/sound_loud.png")

        self.volumeChanged.emit(value)


class PlaybackToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.widget = PlaybackWidget()
        self.addWidget(self.widget)
        self.setMovable(False)
        self.setStyleSheet("background: #181818")


