import yaml

from dataclasses import dataclass
from pathlib import Path
from typing import Any


UTF8 = "utf-8"


# Use this common path to yaml configs directory
config_directory = Path(__file__).resolve().parents[1] / "config"

camera_config_path = config_directory / "camera.yaml"
model_config_path = config_directory / "yolo_model.yaml"
app_config_path = config_directory / "app_config.yaml"


# Helper function used to load yaml files as well as error handle non existent paths
def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding=UTF8) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"CONFIG_ERROR: Invalid YAML structure in {path}")

    return data


# When returning this type to main, configuration values are stored together
@dataclass
class CameraConfig:
    device: int
    width: int
    height: int
    fps: int
    format: str

def load_camera_config() -> CameraConfig:
    data = load_yaml(camera_config_path)["camera"]

    return CameraConfig(
        device = data["device"],
        width = data["width"],
        height = data["height"],
        fps = data["fps"],
        format = data["format"]
    )


# Return the string name of the YOLO model
def load_model_config() -> str:
    return load_yaml(model_config_path)["model"]["name"]


# App configuration values

@dataclass
class LogConfig:
    max_lines: int

@dataclass
class StyleConfig:
    camera_widget: str
    log_widget: str
    app_widget: str

@dataclass
class AppConfig:
    log: LogConfig
    styles: StyleConfig

def load_app_config() -> AppConfig:
    data = load_yaml(app_config_path)

    log = LogConfig(
        max_lines = data["log"]["max_lines"]
        )
    
    styles = StyleConfig(
        camera_widget = data["styles"]["camera_widget"],
        log_widget = data["styles"]["log_widget"],
        app_widget = data["styles"]["app_widget"]
    )

    return AppConfig(
        log,
        styles,
    )