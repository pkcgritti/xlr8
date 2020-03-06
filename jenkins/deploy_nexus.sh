#!/bin/bash

IS_NEXUS_PACKAGE=$(python project.py --is-a nexus_package)

if [ ${IS_NEXUS_PACKAGE} == "True" ];
then
    echo "===== Deploying package on nexus ..."
    jenkins/docker_exec.sh \
        twine upload --repository nexus dist/*
fi
