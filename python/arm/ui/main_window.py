from __future__ import annotations

from PySide6.QtCore import (
    QMetaObject,
    QThread,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QWidget,
)

from arm.vision.camera import Camera
from arm.ui.camera_widget import CameraWidget
from arm.ui.camera_worker import CameraWorker
from arm.config_loader import load_camera_config

class MainWindow(QMainWindow):
    start_camera_requested = Signal()
    stop_camera_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("6-DOF Arm Controller")
        self.resize(1920, 1080)

        self._create_widgets()
        self._create_layout()
        self._create_camera_worker()
        self._connect_signals()

    # Keep the init function small by having all the widgets in a private function
    def _create_widgets(self) -> None:
        self._camera_widget = CameraWidget()

        self._status_label = QLabel("Camera: stopped")

        self._command_input = QLineEdit()
        self._command_input.setPlaceholderText("Enter command")

        self._start_button = QPushButton("Start Camera")
        self._stop_button = QPushButton("Stop Camera")
        self._stop_button.setEnabled(False)

    def _create_layout(self) -> None:
        layout = QGridLayout()

        layout.addWidget(self._camera_widget, 0, 0, 4, 1)
        layout.addWidget(self._status_label, 0, 1)
        layout.addWidget(self._command_input, 1, 1)
        layout.addWidget(self._start_button, 2, 1)
        layout.addWidget(self._stop_button, 3, 1)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    # Create a camera worker private to main window using config values
    def _create_camera_worker(self) -> None:

        camera_config = load_camera_config()

        self._camera_thread = QThread(self)

        self._camera_worker = CameraWorker(
            camera_factory = lambda: Camera(
                camera_config.device,
                camera_config.width,
                camera_config.height,
                camera_config.fps,
                # Required depending on the camera you are using
                camera_config.format
            ),
            capture_fps = camera_config.fps,
        )

        self._camera_worker.moveToThread(self._camera_thread)
        self._camera_thread.start()

    # Separating the camera requests, buttons and the thread to run the camera display
    def _connect_signals(self) -> None:
        self.start_camera_requested.connect(self._camera_worker.start)
        self.stop_camera_requested.connect(self._camera_worker.stop)

        self._start_button.clicked.connect(self.start_camera_requested.emit)
        self._stop_button.clicked.connect(self.stop_camera_requested.emit)

        self._camera_worker.frame_ready.connect(self._camera_widget.set_frame)
        self._camera_worker.started.connect(self._on_camera_started)
        self._camera_worker.stopped.connect(self._on_camera_stopped)
        self._camera_worker.error.connect(self._on_camera_error)

    # Camera start button functionality
    @Slot()
    def _on_camera_started(self) -> None:
        self._status_label.setText("Camera: running")
        self._start_button.setEnabled(False)
        self._stop_button.setEnabled(True)

    # Camera end button functionality
    @Slot()
    def _on_camera_stopped(self) -> None:
        self._camera_widget.clear_frame()
        self._status_label.setText("Camera: stopped")
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)

    @Slot(str)
    def _on_camera_error(self, message: str) -> None:
        self._camera_widget.clear_frame()
        self._status_label.setText(message)
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)

    # Close any threads that are running when exiting the program
    def closeEvent(self, event: QCloseEvent) -> None:
        if self._camera_thread.isRunning():
            QMetaObject.invokeMethod(
                self._camera_worker,
                "stop",
                Qt.ConnectionType.BlockingQueuedConnection,
            )

            self._camera_thread.quit()
            self._camera_thread.wait()

        event.accept()