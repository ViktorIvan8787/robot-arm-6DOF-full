import yaml

from dataclasses import dataclass
from pathlib import Path
from typing import Any

UTF8 = "utf-8"

# Use this common path to yaml configs directory
config_directory = Path(__file__).resolve().parents[1] / "config"

camera_config_path = config_directory / "camera.yaml"
model_config_path = config_directory / "yolo_model.yaml"

# When returning this type to main, configuration values are stored together
@dataclass
class CameraConfig:
    device: int
    width: int
    height: int
    fps: int

# Helper function used to load yaml files as well as error handle non existent paths
def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding=UTF8) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"CONFIG_ERROR: Invalid YAML structure in {path}")

    return data

def load_camera_config() -> CameraConfig:
    data = load_yaml(camera_config_path)["camera"]

    return CameraConfig(
        device = data["device"],
        width = data["width"],
        height = data["height"],
        fps = data["fps"],
    )

# Return the string name of the YOLO model
def load_model_config() -> str:
    return load_yaml(model_config_path)["model"]["name"]