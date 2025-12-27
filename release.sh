#!/bin/bash

set -e

VERSION_FILE="pyproject.toml"
IMAGE_NAME="digital-home-backend"

get_version() {
    grep "^version = " "$VERSION_FILE" | sed 's/version = "\(.*\)"/\1/' | tr -d '"'
}

increment_version() {
    local version=$1
    local part=$2

    IFS='.' read -r major minor patch <<< "$version"

    case $part in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Invalid part. Use: major, minor, or patch"
            exit 1
            ;;
    esac

    echo "${major}.${minor}.${patch}"
}

update_version() {
    local new_version=$1
    sed -i.bak "s/^version = \".*\"/version = \"$new_version\"/" "$VERSION_FILE"
    rm "${VERSION_FILE}.bak"
    echo "Version updated to $new_version"
}

build_docker_image() {
    local version=$1
    local tag=${2:-latest}

    echo "Building Docker image ${IMAGE_NAME}:${tag}..."
    docker build -t "${IMAGE_NAME}:${tag}" .

    if [ "$tag" != "latest" ]; then
        docker tag "${IMAGE_NAME}:${tag}" "${IMAGE_NAME}:latest"
    fi

    echo "Docker image built successfully"
}

push_docker_image() {
    local registry=$1
    local version=$2

    echo "Pushing Docker image to ${registry}..."
    
    docker tag "${IMAGE_NAME}:${version}" "${registry}/${IMAGE_NAME}:${version}"
    docker push "${registry}/${IMAGE_NAME}:${version}"
    
    docker tag "${IMAGE_NAME}:${version}" "${registry}/${IMAGE_NAME}:latest"
    docker push "${registry}/${IMAGE_NAME}:latest"

    echo "Docker image pushed successfully"
}

show_usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  get-version              Get current version"
    echo "  bump <major|minor|patch> Increment version and update pyproject.toml"
    echo "  set <version>            Set specific version"
    echo "  build [tag]              Build Docker image (default tag: current version)"
    echo "  push <registry> [version] Push Docker image to registry"
    echo "  release <major|minor|patch> <registry>  Bump version, build and push"
    echo ""
    echo "Examples:"
    echo "  $0 get-version"
    echo "  $0 bump patch"
    echo "  $0 build v1.0.0"
    echo "  $0 push docker.io/username v1.0.0"
    echo "  $0 release minor docker.io/username"
}

case "$1" in
    get-version)
        get_version
        ;;
    bump)
        if [ -z "$2" ]; then
            echo "Error: Please specify version part (major, minor, or patch)"
            show_usage
            exit 1
        fi
        current_version=$(get_version)
        new_version=$(increment_version "$current_version" "$2")
        update_version "$new_version"
        ;;
    set)
        if [ -z "$2" ]; then
            echo "Error: Please specify version"
            show_usage
            exit 1
        fi
        update_version "$2"
        ;;
    build)
        version=${2:-$(get_version)}
        build_docker_image "$version"
        ;;
    push)
        if [ -z "$2" ]; then
            echo "Error: Please specify registry"
            show_usage
            exit 1
        fi
        registry=$2
        version=${3:-$(get_version)}
        push_docker_image "$registry" "$version"
        ;;
    release)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Error: Please specify version part and registry"
            show_usage
            exit 1
        fi
        current_version=$(get_version)
        new_version=$(increment_version "$current_version" "$2")
        update_version "$new_version"
        build_docker_image "$new_version"
        push_docker_image "$3" "$new_version"
        echo "Release $new_version completed successfully"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
