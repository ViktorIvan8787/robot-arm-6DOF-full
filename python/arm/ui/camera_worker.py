from __future__ import annotations

from collections.abc import Callable
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from cv2 import cvtColor, COLOR_BGR2RGB
from arm.vision.camera import Camera
from arm.config_loader import load_model_config
from ultralytics import YOLO
from arm.vision.detect import *

class CameraWorker(QObject):
    """
    CameraWorker is responsible for managing the camera and capturing frames in a Qt compatible manner.
    It emits signals for frame ready, started, stopped, and error, allowing the worker to run in a separate thread from the main application thread. 
    """

    frame_ready = Signal(object)
    started = Signal()
    stopped = Signal()
    error = Signal(str)

    def __init__(
        self,
        # Create a new camera instance when called
        camera_factory: Callable[[], Camera],
        capture_fps: int,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        # Set up the camera and timer (capture interval based on the desired FPS)
        self._camera_factory = camera_factory
        self._interval_ms = max(1, round(1000 / capture_fps))

        self._camera: Camera | None = None
        self._timer: QTimer | None = None

        self._full_detection_enabled = False

        # Storing the result of detect() as an attribute
        # Easily accessible by the main thread
        self.objectDetected: DetectionResult | None = None

        self._YOLO_Model = YOLO(load_model_config())

    @Slot()
    def start(self) -> None:
        """Open the camera and begin reading frames."""
        if self._camera is not None:
            return

        # Create a new camera instance on start and set a timer
        try:
            self._camera = self._camera_factory()

            if self._timer is None:
                self._timer = QTimer(self)
                self._timer.setInterval(self._interval_ms)
                self._timer.timeout.connect(self._read_frame)

            self._timer.start()
            self.started.emit()

        except Exception as error:
            self._close_camera()
            self.error.emit(str(error))

    @Slot()
    def stop(self) -> None:
        """Stop frame capture and release the camera."""
        was_running = self._camera is not None

        if self._timer is not None:
            self._timer.stop()

        # 
        self._close_camera()

        if was_running:
            self.stopped.emit()

    @Slot()
    def _read_frame(self) -> None:
        """Read and emit a single frame."""
        if self._camera is None:
            return

        try:
            # Read frame, convert to RGB and highlight object
            frame = self._camera.read()
            updated_frame = self._process_frame(frame)

        except Exception as error:
            self.stop()
            self.error.emit(str(error))
            return

        self.frame_ready.emit(updated_frame)

    @Slot(bool)
    def set_full_detection_enabled(self, enabled: bool) -> None:
        """Enable or disable object detection and highlighting."""
        self._full_detection_enabled = enabled

    def _close_camera(self) -> None:
        """Close and discard the current camera instance."""
        if self._camera is None:
            return
        
        self._camera.close()
        self._camera = None

    def _process_frame(self, frame: Frame) -> Frame:
        """Process the frame to highlight objects if full detection is enabled."""
        rgb_frame = cvtColor(frame, COLOR_BGR2RGB)

        if not self._full_detection_enabled:
            return rgb_frame

        detections = analyse(rgb_frame, self._YOLO_Model)
        self.objectDetected = detections

        return highlightObject(rgb_frame, detections)