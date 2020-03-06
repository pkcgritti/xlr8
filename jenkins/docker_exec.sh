#!/bin/sh
# Execute command inside BUILD_IMAGE_URI container

docker run --rm \
  --mount type=bind,source=$(pwd)/git.pem,target=/root/.ssh/id_rsa \
  --mount type=bind,source=$(pwd)/netrc,target=/root/.netrc \
  --mount type=bind,source=$(pwd)/pypirc,target=/root/.pypirc \
  --mount type=bind,source=$(pwd)/pip.conf,target=/root/.pip/pip.conf \
  --mount type=bind,source=$(pwd),target=/build \
  ${BUILD_IMAGE_URI} $*
