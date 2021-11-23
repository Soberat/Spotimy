from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent
from PyQt5.QtWidgets import QToolBar, QHBoxLayout, QPushButton, QWidget, QLabel, QVBoxLayout, QSlider
from Spotify import Track


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
    playPause = pyqtSignal()
    nextTrack = pyqtSignal()
    loopChanged = pyqtSignal(bool)
    volumeChanged = pyqtSignal(int)


    iconSize = 12

    def __init__(self):
        super().__init__()

        self.trackCoverLabel = QLabel()
        self.trackCoverLabel.setPixmap(QPixmap(':/track_placeholder.png').scaled(56, 56, transformMode=Qt.SmoothTransformation))

        self.artistsLabel = QLabel("Magnets")
        self.artistsLabel.setStyleSheet("color:")
        self.titleLabel = QLabel("whoever")

        self.shuffleButton = ToolbarButton(":/shuffle.png", self.iconSize, self.iconSize)

        self.previousButton = ToolbarButton(":/previous.png", self.iconSize, self.iconSize)

        self.playPauseButton = ToolbarButton(":/play.png", 32, 32)
        self.playPauseButton.clicked.connect(self.play_pause_pushed)
        self.statePlaying = False

        self.nextButton = ToolbarButton(":/next.png", self.iconSize, self.iconSize)
        self.nextButton.clicked.connect(lambda: self.nextTrack.emit())

        self.loopButton = ToolbarButton(":/loop.png", self.iconSize, self.iconSize)

        self.trackSlider = QSlider(Qt.Horizontal)
        self.trackSlider.setFixedWidth(700)

        self.queueButton = ToolbarButton(":/queue.png", self.iconSize, self.iconSize)
        self.devicesButton = ToolbarButton(":/connect.png", self.iconSize, self.iconSize)

        self.volumeLabel = QLabel()
        self.volumeLabel.setPixmap(QPixmap(":/sound_mute.png").scaled(self.iconSize, self.iconSize, transformMode=Qt.SmoothTransformation))
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.valueChanged.connect(self.change_volume)
        self.volumeSlider.setFixedWidth(100)
        self.volumeSlider.setSingleStep(1)

        self.maximizeButton = ToolbarButton(":/maximize.png", self.iconSize, self.iconSize)

        layout = QHBoxLayout()

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
        sliderLayout.addWidget(QLabel("0:00"))
        sliderLayout.addWidget(self.trackSlider)
        sliderLayout.addWidget(QLabel("0:00"))
        sliderLayout.addStretch(1000)

        controlLayout.addLayout(innerControlLayout)
        controlLayout.addLayout(sliderLayout)

        layout.addLayout(controlLayout)
        layout.setStretch(2, 100)

        layout.addWidget(self.queueButton)
        layout.addWidget(self.devicesButton)
        layout.addWidget(self.volumeLabel)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.maximizeButton)

        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(2)

        self.setLayout(layout)
        self.setMinimumWidth(1000)

    def set_track(self, track: Track):
        pass

    def play_pause_pushed(self):
        if not self.statePlaying:
            self.playPauseButton.change_pixmap(':/pause.png')
            self.statePlaying = True
        else:
            self.playPauseButton.change_pixmap(':/play.png')
            self.statePlaying = False

    def change_volume(self):
        value = self.volumeSlider.value()
        if value == 0:
            self.volumeLabel.setPixmap(QPixmap(":/sound_mute.png").scaled(self.iconSize, self.iconSize, transformMode=Qt.SmoothTransformation))
        elif value <= 30:
            self.volumeLabel.setPixmap(QPixmap(":/sound_quiet.png").scaled(self.iconSize, self.iconSize, transformMode=Qt.SmoothTransformation))
        elif value <= 70:
            self.volumeLabel.setPixmap(QPixmap(":/sound_normal.png").scaled(self.iconSize, self.iconSize, transformMode=Qt.SmoothTransformation))
        else:
            self.volumeLabel.setPixmap(QPixmap(":/sound_loud.png").scaled(self.iconSize, self.iconSize, transformMode=Qt.SmoothTransformation))

        self.volumeChanged.emit(value)


class PlaybackToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.widget = PlaybackWidget()
        self.addWidget(self.widget)
        self.setMovable(False)
        self.setStyleSheet("background: #181818")

