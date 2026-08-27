#!/usr/bin/env bash
set -euo pipefail

repository_directory="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.."
    pwd
)"

cd "$repository_directory/python"
uv run python -m apps.camera_view