#!/usr/bin/env sh

set -eu

dnf makecache

set +e
dnf check-update --security
if [ $? -eq 100 ]; then
    DNF_SECURITY_UPDATES=1
fi

mkdir -p /output

cat <<EOF >/output/vars
${VAR_PREFIX:-}DNF_SECURITY_UPDATES=${DNF_SECURITY_UPDATES:-0}
EOF
