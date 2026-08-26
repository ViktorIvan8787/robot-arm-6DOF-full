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
        camera_config.fps
    )

    try:
        while True:
            frame = camera.read()
            objects_identified = analyse(frame, yolo_model)
            result = detect(objects_identified, "phone")
    finally:
        camera.close()

if __name__ == "__main__":
    main()