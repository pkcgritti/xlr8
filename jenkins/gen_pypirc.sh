#!/bin/sh
# Generate pypirc ($1 = User, $2 = Pass)

: "${NEXUS_PROTOCOL:="https"}"
: "${NEXUS_HOSTNAME:="services.dev.bancobari.com.br"}"

cat > pypirc <<EOF
[distutils]
index-servers =
    pypi
    nexus

[nexus]
repository: ${NEXUS_PROTOCOL}://${NEXUS_HOSTNAME}/nexus/repository/pypi-hosted/
username: $1
password: $2
EOF
