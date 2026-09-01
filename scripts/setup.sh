#!/usr/bin/env bash

set -euo pipefail

echo "Setting up robot-arm development dependencies..."

if command -v apt-get >/dev/null 2>&1; then
    echo "Detected apt-based Linux distribution."

    sudo apt-get update

    sudo apt-get install -y \
        build-essential \
        cmake \
        git \
        libx11-dev \
        libxcursor-dev \
        libxrandr-dev \
        libxinerama-dev \
        libxi-dev \
        libgl1-mesa-dev \
        libglu1-mesa-dev

elif command -v dnf >/dev/null 2>&1; then
    echo "Detected dnf-based Linux distribution."

    sudo dnf install -y \
        gcc-c++ \
        cmake \
        git \
        libX11-devel \
        libXcursor-devel \
        libXrandr-devel \
        libXinerama-devel \
        libXi-devel \
        mesa-libGL-devel \
        mesa-libGLU-devel

elif command -v pacman >/dev/null 2>&1; then
    echo "Detected pacman-based Linux distribution."

    sudo pacman -S --needed --noconfirm \
        base-devel \
        cmake \
        git \
        libx11 \
        libxcursor \
        libxrandr \
        libxinerama \
        libxi \
        mesa \
        glu

else
    echo "Error: unsupported Linux package manager."
    echo "Please install the required build and Raylib dependencies manually."
    exit 1
fi

echo
echo "Setup complete."
echo "You can now run:"
echo "  ./scripts/simulator.sh"

echo "Syncing python packages for python camera applications..."

sleep 2

repository_directory="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.."
    pwd
)"

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv is not installed."
    echo "Install it with:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Setting up Python environment..."
cd "$repository_directory/python" || exit 1
uv sync

echo "setting up object-detection models..."

sleep 2

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

GROUNDING_DINO_DIR="$PROJECT_ROOT/python/models/grounding_dino"
GROUNDING_DINO_WEIGHTS="$GROUNDING_DINO_DIR/groundingdino_swint_ogc.pth"
GROUNDING_DINO_WEIGHTS_URL="https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"

mkdir -p "$GROUNDING_DINO_DIR"

if [[ -s "$GROUNDING_DINO_WEIGHTS" ]]; then
    echo "Grounding DINO weights already downloaded."
else
    echo "Downloading Grounding DINO weights..."

    TEMP_WEIGHTS="$GROUNDING_DINO_WEIGHTS.part"

    if curl \
        --fail \
        --location \
        --retry 3 \
        --output "$TEMP_WEIGHTS" \
        "$GROUNDING_DINO_WEIGHTS_URL"
    then
        mv "$TEMP_WEIGHTS" "$GROUNDING_DINO_WEIGHTS"
        echo "Grounding DINO weights downloaded successfully."
    else
        rm -f "$TEMP_WEIGHTS"
        echo "Failed to download Grounding DINO weights." >&2
        exit 1
    fi
fi