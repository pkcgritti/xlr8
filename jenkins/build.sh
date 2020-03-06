#!/bin/bash

IS_LAMBDA_FUNCTION=$(python project.py --is-a lambda_function)
IS_LAMBDA_LAYER=$(python project.py --is-a lambda_layer)
IS_NEXUS_PACKAGE=$(python project.py --is-a nexus_package)

if [ ${IS_LAMBDA_FUNCTION} == "True" ];
then
    echo "===== Generating zip package for lambda ..."
    jenkins/docker_exec.sh \
        jenkins/build_kapa.sh
fi

if [ ${IS_LAMBDA_LAYER} == "True" ];
then
    echo "===== Generating package for lambda layer ..."
    jenkins/docker_exec.sh \
        jenkins/build_layer.sh
fi

if [ ${IS_NEXUS_PACKAGE} == "True" ];
then
    echo "===== Generating tar package for nexus ..."
    jenkins/docker_exec.sh \
        python setup.py sdist
fi
