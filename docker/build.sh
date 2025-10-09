#!/bin/bash
set -e

# Configuration
IMAGE_NAME="webcat"
USER="tmfrisinger"
VERSION=2.3.0
TAG="${USER}/${IMAGE_NAME}:${VERSION}"
LATEST="${USER}/${IMAGE_NAME}:latest"
DEFAULT_PORT=8000
PLATFORMS="linux/amd64,linux/arm64"

# Navigate to the root directory
cd "$(dirname "$0")/.."

echo "Building Docker image for FastMCP WebCAT: ${TAG}"
echo "Platforms: ${PLATFORMS}"

# Check if buildx is available
if ! docker buildx version &> /dev/null; then
    echo "Error: docker buildx is not available. Please install it first."
    exit 1
fi

# Create a new builder instance if it doesn't exist
if ! docker buildx ls | grep -q "multiarch"; then
    echo "Creating multiarch builder..."
    docker buildx create --name multiarch --use
fi

# Use the multiarch builder
docker buildx use multiarch

# Build multi-platform image
echo "Building multi-platform image..."
docker buildx build \
    --platform ${PLATFORMS} \
    -t ${TAG} \
    -t ${LATEST} \
    -f docker/Dockerfile \
    --load \
    .

echo "Docker image built successfully!"
echo "To run the Docker image locally:"
echo "docker run -p ${DEFAULT_PORT}:${DEFAULT_PORT} -e SERPER_API_KEY=your_key ${LATEST}"
echo ""
echo "To run on a custom port:"
echo "docker run -p 9000:9000 -e PORT=9000 -e SERPER_API_KEY=your_key ${LATEST}"
echo ""
echo "To customize logging:"
echo "docker run -p ${DEFAULT_PORT}:${DEFAULT_PORT} -e SERPER_API_KEY=your_key -e LOG_LEVEL=DEBUG ${LATEST}"
echo ""
echo "To push to a registry, run:"
echo "docker buildx build --platform ${PLATFORMS} -t ${TAG} -t ${LATEST} -f docker/Dockerfile --push ."
echo ""
echo "Note: Use --push flag with buildx to push multi-platform images to registry"
