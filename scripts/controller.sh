#!/usr/bin/env bash

set -e

repository_directory="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.."
    pwd
)"

cd "$repository_directory/python"
exec uv run python -m apps.arm_controller