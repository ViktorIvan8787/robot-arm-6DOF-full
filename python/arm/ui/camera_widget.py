from __future__ import annotations

import cv2 as cv

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel
from arm.vision.camera_types import Frame
# Note: Chaining down the YOLO import
from arm.vision.detect import highlightObject, analyse, YOLO
from arm.config_loader import load_model_config

class CameraWidget(QLabel):
    """
    Camera widget for setting, clearing frames and updating displays

    Stores the frame as QPixmap for maximum editability on the image
    """

    # Store a QPixmap for the newest frame to be added
    # YOLO model embedded into the camera widget, required for object detection
    def __init__(self) -> None:
        super().__init__("Camera stopped")

        self._YOLOModel = YOLO(load_model_config())
        self._source_pixmap: QPixmap | None = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(1280, 720)
        self.setMaximumSize(1280, 720)
        self.setStyleSheet(
            """
            QLabel {
                background-color: #202020;
                color: #d0d0d0;
                border: 1px solid #505050;
            }
            """
        )

    # Frame is received and processed under object highlighting
    # Essential attributes are set before setting the source pixel map
    @Slot(object)
    def set_frame(self, frame: Frame) -> None:
        """Convert and display an OpenCV BGR frame"""
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        updated_frame = highlightObject(rgb_frame, analyse(rgb_frame, self._YOLOModel))

        height, width, channels = updated_frame.shape
        bytes_per_line = width * channels

        image = QImage(
            updated_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        ).copy()

        self._source_pixmap = QPixmap.fromImage(image)
        self._update_display()

    @Slot()
    def clear_frame(self) -> None:
        """Clear the displayed frame"""
        self._source_pixmap = None
        self.clear()
        self.setText("Camera stopped")

    # Resize the widget screen to the maximum size (set in attributes)
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Resize the camera window from min size to max size when camera is started"""
        super().resizeEvent(event)
        self._update_display()

    def _update_display(self) -> None:
        if self._source_pixmap is None:
            return

        displayed_pixmap = self._source_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(displayed_pixmap)