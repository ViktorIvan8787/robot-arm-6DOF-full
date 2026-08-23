# Code for camera to detect objects using YOLO [Currently only detects "cup" (there is no input right now)]

import cv2
import numpy as np

from camera import Camera
from ultralytics import YOLO
from dataclasses import dataclass
from numpy.typing import NDArray

# Custom Data type for a frame, which is a numpy array of uint8 values
Frame = NDArray[np.uint8]

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

# Function to load the model 
def load_model(model_path: str = "yolov8n.pt") -> YOLO:
    """Load the YOLO model from the specified path."""
    return YOLO(model_path)

# Function to capture the frame 
def capture_frame(camera: Camera) -> Frame:
    """Capture a single still frame using camera class functions."""
    return camera.read()

# Function to analyse the frame and produce a list of detected objects
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

# Open camera make sure that it reads frame properly and capture the frame
# Capture a still image from the video camera {default camera: 0} 
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

# Check if the frame was read correctly using the ret variable
if not ret :
    raise RuntimeError("Failed to capture image")

# Otherwise we can pass the frame into the model and start detecting
cv2.imwrite("captured_frame.jpg", frame)

# Get the results of passing the captured frame into the model 
results = model("captured_frame.jpg")

# Iterate over the results and find the object that you are looking for 

target_class = "cup"

for image in results:
    for object in image.boxes:
        # get the class name of the object to compare to the target class
        class_name = model.name[int(object.cls[0])]
        # get the confidence for this object 
        confidence = float(object.conf[0])

        # check if it is the right object
        if target_class == class_name:
            # Get centre coordinates of the object
            x , y , _ , _ = object.xywh[0]
            # Print out that object has been found for test units and debugging
            print(f"{target_class} object found, (conf {confidence:.2f}) at pixel coordinates ({x:.0f}, {y:.0f})")