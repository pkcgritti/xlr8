#!/bin/sh
# Create layer with project requirements and all files inside src/
# directory
PACKAGE_PATH="python/lib/python3.8/site-packages"

# Install dependencies locally
mkdir -p $PACKAGE_PATH
pip install . -t $PACKAGE_PATH

# Cleanup dist
rm -rf $PACKAGE_PATH/*dist-info \
    $PACKAGE_PATH/bin

find "$PACKAGE_PATH" -path "*tests" | xargs rm -rf
find "$PACKAGE_PATH" -name "*.so" | xargs strip

# Zip layer
zip -r layer.zip python
