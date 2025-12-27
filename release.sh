#!/bin/bash

set -e

VERSION_FILE="pyproject.toml"
IMAGE_NAME="digital-home-backend"

get_version() {
    grep "^version = " "$VERSION_FILE" | sed 's/version = "\(.*\)"/\1/' | tr -d '"'
}

build_docker_image() {
    local version=$(get_version)

    echo "Building Docker image ${IMAGE_NAME}:${version}..."
    docker build -t "${IMAGE_NAME}:${version}" .

    echo "Docker image built successfully: ${IMAGE_NAME}:${version}"
}

push_docker_image() {
    local registry=$1
    local version=$2

    echo "Pushing Docker image to ${registry}..."
    
    docker tag "${IMAGE_NAME}:${version}" "${registry}/${IMAGE_NAME}:${version}"
    docker push "${registry}/${IMAGE_NAME}:${version}"

    echo "Docker image pushed successfully"
}

show_usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  get-version              Get current version from pyproject.toml"
    echo "  build                    Build Docker image (tag = version from pyproject.toml)"
    echo "  push <registry>          Push Docker image to registry (uses current version)"
    echo ""
    echo "Notes:"
    echo "  - Version is always read from pyproject.toml"
    echo "  - Edit pyproject.toml directly to change version"
    echo "  - Docker tag always equals the version from pyproject.toml"
    echo "  - Latest tag is automatically created for every build"
    echo ""
    echo "Examples:""
    echo "  - Latest tag is automatically created for every build
    echo "  $0 get-version"
    echo "  $0 build"
    echo "  $0 push docker.io/username"
}

case "$1" in
    get-version)
        get_version
        ;;
    build)
        build_docker_image
        ;;
    push)
        if [ -z "$2" ]; then
            echo "Error: Please specify registry"
            show_usage
            exit 1
        fi
        registry=$2
        version=$(get_version)
        push_docker_image "$registry" "$version"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
