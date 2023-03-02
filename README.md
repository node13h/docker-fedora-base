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
  FEDORA_IMAGE=docker.io/alikov/fedora-base-amd64 \
  FEDORA_VERSION=37-1677710279 \
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
by starting a container using `docker.io/alikov/fedora-base-amd64:37-1677710279`,
installing same packages as on the native machine, then executing
`dnf makecache && dnf check-update` in that container.
