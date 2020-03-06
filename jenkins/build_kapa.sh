#!/bin/sh

# Activate virtual environment
if [ -d "ci_env" ]; then
    echo "Activating virtualenv"
    . ci_env/bin/activate
fi

# Execute
kapa build
