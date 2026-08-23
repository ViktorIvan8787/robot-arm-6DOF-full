from .camera import Camera
from ultralytics import YOLO # type: ignore
from dataclasses import dataclass
from .camera_types import Frame

# Custom data class to hold the detection
@dataclass
class Detection:
    class_name: str
    confidence: float
    centre_x: float
    centre_y: float

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
            centre_x, centre_y, _,_ = box.xywh[0]
            detections.append(Detection(class_name, confidence, float(centre_x), float(centre_y)))
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