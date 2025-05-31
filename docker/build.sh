#!/bin/bash
set -e

# Configuration
IMAGE_NAME="webcat"
USER="tmfrisinger"
VERSION=1.2.1
TAG="${USER}/${IMAGE_NAME}:${VERSION}"
LATEST="${USER}/${IMAGE_NAME}:latest"
DEFAULT_PORT=8000

# Navigate to the root directory
cd "$(dirname "$0")/.."

echo "Building Docker image for FastAPI WebCAT: ${TAG}"
docker build -t ${TAG} -t ${LATEST} -f docker/Dockerfile .

echo "Docker image built successfully!"
echo "To run the Docker image locally:"
echo "docker run -p ${DEFAULT_PORT}:${DEFAULT_PORT} -e SERPER_API_KEY=your_key ${LATEST}"
echo ""
echo "To run on a custom port:"
echo "docker run -p 9000:9000 -e PORT=9000 -e SERPER_API_KEY=your_key ${LATEST}"
echo ""
echo "To customize rate limiting:"
echo "docker run -p ${DEFAULT_PORT}:${DEFAULT_PORT} -e SERPER_API_KEY=your_key -e RATE_LIMIT_WINDOW=60 -e RATE_LIMIT_MAX_REQUESTS=10 ${LATEST}"
echo ""
echo "To push to a registry, run:"
echo "docker push ${TAG}"
echo "docker push ${LATEST}"

# Uncomment the following lines if you want to automatically push to a registry
# docker push ${TAG}
# docker push ${LATEST}
# echo "Docker image pushed successfully!" 