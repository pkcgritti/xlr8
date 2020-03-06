#!/bin/sh
# Create a virtualenv for this project

if ! [ -d "ci_env" ];
then
    virtualenv ci_env
    . ci_env/bin/activate
    pip install -r requirements-dev.txt
    pip install pytest pytest-cov pylint
    pip install -e .
fi
