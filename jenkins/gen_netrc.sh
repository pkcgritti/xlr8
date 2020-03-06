#!/bin/sh
# Generate netrc ($1 = User, $2 = Pass)

: "${NEXUS_HOSTNAME:="services.dev.bancobari.com.br"}"

cat > netrc <<EOF
machine ${NEXUS_HOSTNAME}
    login $1
    password $2
EOF
