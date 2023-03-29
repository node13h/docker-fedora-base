#!/usr/bin/env sh

set -eux

if [ "${FORCE_BUILD:-}" = "1" ]; then
    exit 1
fi

if [ "${x86_64_DNF_SECURITY_UPDATES:-}" = "1" ]; then
    exit 1
fi

if [ "${aarch64_DNF_SECURITY_UPDATES:-}" = "1" ]; then
    exit 1
fi

printf 'There are no reasons to run the build. Skipping.\n' >&2

exit 0
