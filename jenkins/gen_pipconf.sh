#!/bin/sh
# Generate pipconf

: "${NEXUS_PROTOCOL:="https"}"
: "${NEXUS_HOSTNAME:="services.dev.bancobari.com.br"}"
: "${NEXUS_REPONAME:="pypi-hosted"}"

cat > pip.conf <<EOF
[global]
index = ${NEXUS_PROTOCOL}://${NEXUS_HOSTNAME}/nexus/repository/pypi-group/pypi
index-url = ${NEXUS_PROTOCOL}://${NEXUS_HOSTNAME}/nexus/repository/pypi-group/simple
trusted-host = ${NEXUS_HOSTNAME}
EOF
