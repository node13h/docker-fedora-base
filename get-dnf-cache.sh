#!/usr/bin/env sh

set -eu

if [ "$DO_REFRESH" = "1" ]; then
    dnf -y makecache
fi

mkdir -p /build

(
    cd /var/cache/dnf

    dnf repolist --enabled | tail -n +2 | while read -r repo_id _; do
        printf -- '%s\n' "${repo_id}"-????????????????/
    done | sort | tar -czf /build/dnf-cache.tar.gz \
                      --sort=name \
                      --mtime="@${SOURCE_DATE_EPOCH}" \
                      --owner=0 --group=0 --numeric-owner \
                      --files-from -
)
