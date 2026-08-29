import cv2 as cv

from arm.vision.camera import Camera
from arm.vision.detect import *
from arm.config_loader import load_camera_config, load_model_config

def main() -> None:
    
    # Load configs
    camera_config = load_camera_config()
    model_tag = load_model_config()
    yolo_model = YOLO(model_tag)

    camera = Camera(
        camera_config.device,
        camera_config.width,
        camera_config.height,
        camera_config.fps,
        # Required depending on the camera you are using
        camera_config.format
    )

    # Loop can be set to false if user presses the button to quit camera application
    loop = True

    try:
        while loop:
            frame = camera.read()
            objects_identified = analyse(frame, yolo_model)
            # result = detect(objects_identified, "")
            loop = camera.display(objects_identified, frame)
    finally:
        camera.close()
        cv.destroyAllWindows()

if __name__ == "__main__":
    main()