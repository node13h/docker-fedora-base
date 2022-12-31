ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG DNF_CACHE_TARBALL
ADD $DNF_CACHE_TARBALL /var/cache/dnf

COPY --chown=root:root deterministic-update.sh /usr/local/bin/deterministic-update.sh
ARG SOURCE_DATE_EPOCH
RUN sh /usr/local/bin/deterministic-update.sh
