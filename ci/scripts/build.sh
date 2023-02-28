#!/usr/bin/env sh

set -eux

rm -rf dnf-cache ci/tmp
mkdir -p ci/tmp

./dnf-cache.py \
    --log-level DEBUG --version "$FEDORA_VERSION" \
    new \
    "registry.fedoraproject.org/fedora:${FEDORA_VERSION}" "fedora-${ARCH}-${FEDORA_VERSION}"

./build-image.py \
    --log-level DEBUG \
    --push \
    --output-file "$OUTPUT_METADATA_FILE" \
    "${CONTAINER_REGISTRY}/${IMAGE_NAMESPACE%/}/fedora-base-${ARCH}" "fedora-${ARCH}-${FEDORA_VERSION}"
