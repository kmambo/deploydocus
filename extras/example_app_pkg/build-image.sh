#!/usr/bin/env bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
docker build "${SCRIPT_DIR}" -t python-httpserver
kind load docker-image  python-httpserver:latest -n deploydocus
