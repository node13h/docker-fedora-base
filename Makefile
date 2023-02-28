FEDORA_IMAGE := registry.fedoraproject.org/fedora
FEDORA_VERSION := 37
# Assume host arch is the same as build arch.
ARCH := $(shell arch)
IMAGE_NAME := fedora-base

.PHONY: dnf-cache build clean

dnf-cache/fedora-$(FEDORA_VERSION)-$(ARCH).json:
	./dnf-cache.py --log-level DEBUG --version $(FEDORA_VERSION) new $(FEDORA_IMAGE):$(FEDORA_VERSION) fedora-$(FEDORA_VERSION)-$(ARCH)

dnf-cache: dnf-cache/fedora-$(FEDORA_VERSION)-$(ARCH).json

build: dnf-cache/fedora-$(FEDORA_VERSION)-$(ARCH).json
	./build-image.py --log-level DEBUG $(IMAGE_NAME) fedora-$(FEDORA_VERSION)-$(ARCH)

clean:
	rm -rf dnf-cache
