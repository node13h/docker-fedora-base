#!/usr/bin/env sh

set -eux

MANIFEST="${CONTAINER_REGISTRY}/${IMAGE_NAMESPACE%/}/fedora-base:${FEDORA_VERSION}"

if podman image exists "$MANIFEST"; then
    podman image rm "$MANIFEST"
fi

if podman manifest exists "$MANIFEST"; then
    podman manifest rm "$MANIFEST"
fi

AMD64_IMAGE=$(jq -er .image <"$AMD64_METADATA_FILE")
ARM64_IMAGE=$(jq -er .image <"$ARM64_METADATA_FILE")

podman manifest create "$MANIFEST"
podman manifest add "$MANIFEST" "docker://${AMD64_IMAGE}"
podman manifest add "$MANIFEST" "docker://${ARM64_IMAGE}"
podman manifest push "$MANIFEST" "docker://${MANIFEST}"
