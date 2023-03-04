# docker-fedora-base

This repo does deterministic builds of Fedora Linux with latest updates
applied. Starting from Fedora 37, builds should be bit-for-bit reproducible.
Versions below 37 - not completely, but very close.

DNF cache is retained in the image, and commands like `dnf install` will
install the cached package versions (if they're still available in the mirror)
instead of the latest ones (unless the cache is rebuilt).

Beware, that the Fedora mirror selected during the build will end up in the
cache and dnf commands executed in the future will pull use it.

As old package versions are removed from Fedora mirrors, some older image
tags may become non-rebuildable. This can be solved by hosting your
own mirror with old packages retained.

New images are built in CI when there are new security updates available.

## Project goals

- Proof of concept for bit-for-bit reproducible container image builds.
- Source for point-in-time snapshots of DNF metadata cache. Useful for
  deterministic updates of native (non-containerised) Fedora machines (see
  below).

## Using DNF cache from images for deterministic native OS updates

The following example assumes `x86_64` architecture.

```sh
make clean dnf-cache \
  FEDORA_IMAGE=docker.io/alikov/fedora-base-x86_64:37-1677949231 \
  CACHE_OP=extract
```
This will save a tarball with DNF cache in `dnf-cache/fedora-37-x86_64.tar.gz`

On the destination machine:

- Extract `fedora-37-x86_64.tar.gz` (or `fedora-37-aarch64.tar.gz`)
  to `/var/cache/dnf`.

- Set `metadata_expire=-1` and `check_config_file_age=False`
  in `/etc/dnf/dnf.conf`:

- Comment out the `metadata_expire` setting in `/etc/yum.repos.d/*.repo` files.

- Run `dnf update`.

That's it. Later on you can check if there are any updates available _locally_
by starting a container using `docker.io/alikov/fedora-base-x86_64:37-1677949231`,
installing same packages as on the native machine, then executing
`dnf makecache && dnf check-update` in that container.


## Reproducing a build

This is only going to work with Fedora 37 or later.

The following example will reproduce
`docker.io/alikov/fedora-base-x86_64:37-1677949231` locally. The existing image
will be used as DNF the cache source.

```sh
# Save the existing image digest for later comparison.
ORIGINAL_DIGEST=$(skopeo inspect docker://docker.io/alikov/fedora-base-x86_64:37-1677949231 \
                    | jq -re .Digest)

# Check out the same Git commit as the image was built from.
GIT_SHA=$(skopeo inspect docker://docker.io/alikov/fedora-base-x86_64:37-1677949231 \
            | jq -er '.Labels."com.alikov.image.ref"')
git checkout "$GIT_SHA"

# Fetch the DNF cache and some metadata (timestamp, base image, version) from the
# existing image.
make clean dnf-cache \
  FEDORA_IMAGE=docker.io/alikov/fedora-base-x86_64:37-1677949231 \
  CACHE_OP=extract

# Remove all images, otherwise some existing layers might get reused and affect
# the build purity.
podman image prune --all --force

# Build.
make build IMAGE_NAME=docker.io/alikov/fedora-base-x86_64

BUILD_DIGEST=$(skopeo inspect containers-storage:docker.io/alikov/fedora-base-x86_64:37-1677949231 \
                 | jq -re .Digest)

if [ -n "$ORIGINAL_DIGEST" ] && [ "$ORIGINAL_DIGEST" = "$BUILD_DIGEST" ]; then
  echo Image digests match!
fi
```
