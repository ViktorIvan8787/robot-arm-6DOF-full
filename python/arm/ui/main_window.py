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
    QLineEdit,
    QMainWindow,
    QPushButton,
    QWidget,
    QHBoxLayout,
)

from arm.vision.camera import Camera

from arm.ui.camera_widget import CameraWidget
from arm.ui.camera_worker import CameraWorker
from arm.ui.log_widget import LogWidget, LogLevel, Colour

from arm.config_loader import load_camera_config, load_app_config

APP_CONFIG = load_app_config()
CAMERA_CONFIG = load_camera_config()

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

    # Private layout/widget setup functions

    # Keep the init function small by having all the widgets in a private function
    def _create_widgets(self) -> None:
        self._camera_widget = CameraWidget(APP_CONFIG.styles.camera_widget)

        self._log_widget = LogWidget(
            APP_CONFIG.styles.log_widget,
            APP_CONFIG.log.max_lines
        )

        # Input box for user input
        self._command_input = QLineEdit()
        self._command_input.setObjectName("commandInput")
        self._command_input.setPlaceholderText("Enter command")

        # Buttons for the controller
        self._submit_button = QPushButton("Submit")
        self._submit_button.setObjectName("submitButton")
        self._submit_button.setEnabled(False)
        self._detection_button = QPushButton("Full Detection")
        self._clear_log_button = QPushButton("Clear Log")
        self._link_arm_button = QPushButton("Link Arm")

        self._start_button = QPushButton("Start Camera")
        self._stop_button = QPushButton("Stop Camera")
        # Set stop button initially to false, so that it is disabled by default
        self._stop_button.setEnabled(False)

    def _create_layout(self) -> None:
        main_layout = QGridLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setHorizontalSpacing(14)
        main_layout.setVerticalSpacing(14)

        # Main camera and log area
        main_layout.addWidget(self._camera_widget, 0, 0)
        main_layout.addWidget(self._log_widget, 0, 1)

        # Embedded command bar
        command_bar = QWidget()
        command_bar.setObjectName("commandBar")
        command_bar.setFixedHeight(58)

        command_layout = QHBoxLayout(command_bar)
        command_layout.setContentsMargins(0, 0, 0, 0)
        command_layout.setSpacing(0)

        command_layout.addWidget(self._command_input, 1)
        command_layout.addWidget(self._submit_button)

        main_layout.addWidget(command_bar, 1, 0)

        # Main control buttons
        controls_widget = QWidget()
        controls_layout = QGridLayout(controls_widget)

        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setHorizontalSpacing(14)
        controls_layout.setVerticalSpacing(12)

        controls_layout.addWidget(self._start_button, 0, 0)
        controls_layout.addWidget(self._detection_button, 0, 1)
        controls_layout.addWidget(self._link_arm_button, 0, 2)

        controls_layout.addWidget(self._stop_button, 1, 0)
        controls_layout.addWidget(self._clear_log_button, 1, 1)

        controls_layout.setColumnStretch(0, 1)
        controls_layout.setColumnStretch(1, 1)
        controls_layout.setColumnStretch(2, 1)

        main_layout.addWidget(controls_widget, 2, 0)

        # Camera area is approximately twice as wide as the log.
        main_layout.setColumnStretch(0, 2)
        main_layout.setColumnStretch(1, 1)

        # Let the camera/log row consume extra vertical space.
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 0)
        main_layout.setRowStretch(2, 0)

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        central_widget.setLayout(main_layout)

        central_widget.setStyleSheet(
            "\n".join(
                (
                    APP_CONFIG.styles.app_widget,
                    APP_CONFIG.styles.button_widget,
                    APP_CONFIG.styles.command_bar,
                )
            )
        )

        self.setCentralWidget(central_widget)

    # Separating the camera requests, buttons and the thread to run the camera display
    def _connect_signals(self) -> None:
        # Camera requests
        self.start_camera_requested.connect(self._camera_worker.start)
        self.stop_camera_requested.connect(self._camera_worker.stop)

        # Button signals
        self._start_button.clicked.connect(self.start_camera_requested.emit)
        self._stop_button.clicked.connect(self.stop_camera_requested.emit)

        self._command_input.textChanged.connect(self._update_submit_button)
        self._submit_button.clicked.connect(self._on_submit_button_clicked)
        self._clear_log_button.clicked.connect(self._log_widget.clear_log)

        # Camera worker functionality
        self._camera_worker.frame_ready.connect(self._camera_widget.set_frame)
        self._camera_worker.started.connect(self._on_camera_started)
        self._camera_worker.stopped.connect(self._on_camera_stopped)
        self._camera_worker.error.connect(self._on_camera_error)

    # Camera worker functionality

    # Create a camera worker private to main window using config values
    def _create_camera_worker(self) -> None:
        self._camera_thread = QThread(self)

        self._camera_worker = CameraWorker(
            camera_factory = lambda: Camera(
                CAMERA_CONFIG.device,
                CAMERA_CONFIG.width,
                CAMERA_CONFIG.height,
                CAMERA_CONFIG.fps,
                # Required depending on the camera you are using
                CAMERA_CONFIG.format
            ),
            capture_fps = CAMERA_CONFIG.fps,
        )

        self._camera_worker.moveToThread(self._camera_thread)
        self._camera_thread.start()

    # Camera start button functionality
    @Slot()
    def _on_camera_started(self) -> None:
        self._log_widget.addLine(LogLevel.INFO, "camera running")
        self._start_button.setEnabled(False)
        self._stop_button.setEnabled(True)

    # Camera end button functionality
    @Slot()
    def _on_camera_stopped(self) -> None:
        self._log_widget.addLine(LogLevel.INFO, "camera stopped", Colour.YELLOW)
        self._camera_widget.clear_frame()
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)

    @Slot(str)
    def _on_camera_error(self, message: str) -> None:
        self._camera_widget.clear_frame()
        self._status_label.setText(message)
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)

    # Command input functionality

    def _update_submit_button(self) -> None:
        if self._command_input.text():
            self._submit_button.setEnabled(True)
        else:
            self._submit_button.setEnabled(False)

    def _on_submit_button_clicked(self) -> None:

        input_text = self._command_input.text()
        
        # Handling empty command input
        if len(input_text) == 0:
            return

        self._log_widget.addLine(LogLevel.CMD, input_text)
        self._log_widget.addLine(LogLevel.DEBUG, "parsing command data...")
        self._command_input.clear()
        
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