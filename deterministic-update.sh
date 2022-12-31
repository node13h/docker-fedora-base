#!/usr/bin/env sh

set -eu


main () {
    sed -e /^metadata_expire=-1/d \
        -e /^check_config_file_age=/d \
        -i \
        /etc/dnf/dnf.conf

    cat <<EOF >>/etc/dnf/dnf.conf
metadata_expire=-1
check_config_file_age=False
EOF

    sed -i s/^metadata_expire/#metadata_expire/ /etc/yum.repos.d/*.repo

    dnf update -y

    rm -f /var/cache/dnf/*.solv /var/cache/dnf/*.solvx

    find /var/cache/dnf -type d -name packages -delete

    truncate --size=0 \
             /var/log/dnf.librepo.log \
             /var/log/dnf.log \
             /var/log/dnf.rpm.log \
             /var/log/hawkey.log \
             /usr/lib/sysimage/rpm/rpmdb.sqlite-shm

    rm -f /var/lib/dnf/history.sqlite* /var/cache/ldconfig/aux-cache
}


if ! (return 2> /dev/null); then
    main "$@"
fi
