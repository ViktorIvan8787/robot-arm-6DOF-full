import cv2
import warnings

from camera.camera_types import Frame

class Camera:
    """Manage frame capture from an OpenCV-compatible camera.

    Configures the requested resolution and frame rate, validates the
    resulting camera settings, and manages frame acquisition and release.
    """

    # Obtain the camera device settings 
    # Set properties from camera config and validate those properties
    def __init__(self,
        device: int,
        width: int,
        height: int,
        fps: int
    ) -> None:
        self._capture = cv2.VideoCapture(device)

        if not self._capture.isOpened():
            raise RuntimeError(
                f"CAM_ERROR: Could not open camera {device}"
            )
        
        # Identify and set the different camera properties
        # These include, width, height
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._capture.set(cv2.CAP_PROP_FPS, fps)

        # Obtain camera property values using property ID
        actual_width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH, width)
        actual_height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_fps = self._capture.get(cv2.CAP_PROP_FPS, fps)
    
        # Incorrect width and height means calibration will not be correct
        if actual_width != width and actual_height != height:
            raise RuntimeError(
                "CAM_ERROR: Could not set width and height to 720p settings"
            )
        
        # Raise warning for incorrect fps as it wont affect results
        # Incorrect fps is anything less than the config value
        if actual_fps < fps:
            warnings.warn(
                "CAM_WARNING: Camera FPS differs from requested FPS",
                RuntimeWarning,
            )

    # Returns a single frame, if it cannot then raise an error
    def read(self) -> Frame:
        """Return one singular image frame"""
        success, frame = self._capture.read(self)

        if not success:
            raise RuntimeError(
                "CAM_ERROR: Could not return frame from camera"
            )
        
        return frame
    
    def close(self) -> None:
        """Free camera usage by clearing capture property"""
        self._capture.release()