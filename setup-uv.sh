#!/bin/bash
# UV setup script to handle mirror source issues
# UV 配置脚本，解决镜像源问题

echo "Setting up UV with official PyPI mirror..."
export UV_INDEX_URL=https://pypi.org/simple
export UV_EXTRA_INDEX_URL=https://pypi.org/simple

# If no arguments provided, run uv sync
if [ $# -eq 0 ]; then
    echo "Running: uv sync --no-dev"
    uv sync --no-dev
else
    echo "Running: uv $*"
    uv "$@"
fi