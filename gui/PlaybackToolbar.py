from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent
from PyQt5.QtWidgets import QToolBar, QHBoxLayout, QPushButton, QWidget, QLabel, QVBoxLayout, QProgressBar, QSlider, \
    QFrame
from Spotify import Track
import resources


class PlaybackControlButton(QWidget):

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

    volumeChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.trackCoverLabel = QLabel()
        self.trackCoverLabel.setPixmap(QPixmap(':/track_placeholder.png'))

        self.artistsLabel = QLabel("Magnets")
        self.titleLabel = QLabel("whoever")

        self.shuffleButton = PlaybackControlButton(":/shuffle.png", 16, 16)

        self.previousButton = PlaybackControlButton(":/previous.png", 16, 16)

        self.playPauseButton = PlaybackControlButton(":/play.png", 32, 32)
        self.playPauseButton.clicked.connect(self.play_pause_pushed)
        self.statePlaying = False

        self.nextButton = PlaybackControlButton(":/next.png", 16, 16)

        self.loopButton = PlaybackControlButton(":/loop.png", 16, 16)

        self.volumeLabel = QLabel()
        self.volumeLabel.setPixmap(QPixmap(":/sound_mute.png").scaled(20, 20, transformMode=Qt.SmoothTransformation))
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.valueChanged.connect(self.change_volume)
        self.volumeSlider.setFixedWidth(75)
        self.volumeSlider.setStyleSheet("QSlider::sub-page:horizontal {background: #1db954; height: 40px;} QSlider::handle:horizontal {image: url(:/slider_handle.png);margin: -3px 0;} QSlider::groove:horizontal {border-radius: 2px}")

        self.maximizeButton = QPushButton()
        self.maximizeButton.setIcon(QIcon(":/maximize.png"))

        layout = QHBoxLayout()

        layout.addWidget(self.trackCoverLabel)

        innerLayout = QVBoxLayout()
        innerLayout.addWidget(self.titleLabel)
        innerLayout.addWidget(self.artistsLabel)

        layout.addLayout(innerLayout)

        controlLayout = QVBoxLayout()
        frame = QFrame()
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
        slider = QSlider(Qt.Horizontal)
        slider.setFixedWidth(700)
        slider.setStyleSheet(
            "QSlider::sub-page:horizontal {background: #1db954; height: 40px;} QSlider::handle:horizontal {image: url(:/slider_handle.png);margin: -3px 0;} QSlider::groove:horizontal {border-radius: 2px}")
        slider.setShortcutEnabled(True)
        sliderLayout.addWidget(slider)
        sliderLayout.addWidget(QLabel("0:00"))
        sliderLayout.addStretch(1000)

        controlLayout.addLayout(innerControlLayout)
        controlLayout.addLayout(sliderLayout)

        layout.addLayout(controlLayout)
        layout.setStretch(2, 100)

        layout.addWidget(self.volumeLabel)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.maximizeButton)

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
            self.volumeLabel.setPixmap(QPixmap(":/sound_mute.png").scaled(20, 20, transformMode=Qt.SmoothTransformation))
        elif value <= 30:
            self.volumeLabel.setPixmap(QPixmap(":/sound_quiet.png").scaled(20, 20, transformMode=Qt.SmoothTransformation))
        elif value <= 70:
            self.volumeLabel.setPixmap(QPixmap(":/sound_normal.png").scaled(20, 20, transformMode=Qt.SmoothTransformation))
        else:
            self.volumeLabel.setPixmap(QPixmap(":/sound_loud.png").scaled(20, 20, transformMode=Qt.SmoothTransformation))

        self.volumeChanged.emit(value)


class PlaybackToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.addWidget(PlaybackWidget())
        self.setMovable(False)
        self.setStyleSheet("background: #282828")


