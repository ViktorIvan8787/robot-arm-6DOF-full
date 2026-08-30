from cv2 import (
    rectangle,
    putText,
    FONT_HERSHEY_SIMPLEX,
)

from typing import Tuple
from ultralytics import YOLO # type: ignore
from dataclasses import dataclass
from .camera_types import Frame

# Custom data class to hold the detection
@dataclass
class Detection:
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

# Custom data class to hold Detection result
@dataclass
class DetectionResult:
    found: bool
    detection: Detection | None # if no detection was found

# Analyse the frame and produce a list of detected objects
def analyse(frame: Frame, model: YOLO) -> list[Detection]:
    """Pass the frame into the YOLO mdoel to detect the different objects and produce a list of these objects"""

    results = model(frame)
    detections = []

    for result in results:
        for box in result.boxes:
            class_name = model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detections.append(Detection(class_name, confidence, x1, y1, x2, y2))
    return detections

# Return a dataclass with a found flag to signify if target object has been detected
def detect(detections: list[Detection], target_class: str, min_confidence: float = 0.5) -> DetectionResult:
    """Chose the detection that has the same class name as the target class and has the highest confidence"""

    # List comprehension to filter out any detected objects that do not match the criteria
    candidates = [d for d in detections if d.class_name == target_class and d.confidence >= min_confidence]

    # If there are no candidates then return False
    if not candidates:
        return DetectionResult(False, None)

    # Otherwise pick the best match (detection with highest confidence)
    best_match = max(candidates, key = lambda d: d.confidence)
    return DetectionResult(True, best_match)

def highlightObject(frame: Frame, objects: list[Detection], target_object: Detection = None) -> Frame:
    """Highlight the all objects detected on the camera window"""

    if not objects:
        return frame
    
    colour: tuple[int, int, int]

    # Every object detected will be pinpointed on the camera window
    for obj in objects:
        # Highlight target object with blue
        if target_object == obj:
            colour = (0, 0, 255)
        else: 
            # Change the colour based on the confidence
            colour = (255 - obj.confidence * 255, obj.confidence * 255, 0)

        new_frame = rectangle(frame, (obj.x1, obj.y1), (obj.x2, obj.y2), colour, 3)
        new_frame = putText(frame, obj.class_name, (obj.x1 + 5, obj.y1 + 15), FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return new_frame