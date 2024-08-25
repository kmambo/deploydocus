#!/usr/bin/env bash
set -euxo pipefail

IMAGE_NAME=python-jsonserver
REMOTE_IMG_TAG=docker.io/pbhowmic/python-jsonserver:0.1

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
docker build "${SCRIPT_DIR}" -t ${IMAGE_NAME}
docker tag ${IMAGE_NAME} ${REMOTE_IMG_TAG}
docker push ${REMOTE_IMG_TAG}
#kind load docker-image  ${IMAGE_NAME} -n deploydocus
