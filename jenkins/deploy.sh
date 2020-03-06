#!/bin/bash

ENVIRONMENT_NAME=$1

if [ -z $ENVIRONMENT_NAME ];
then
    ENVIRONMENT_NAME="default"
fi

ACCOUNT_ID=$(aws --profile ${ENVIRONMENT_NAME} sts get-caller-identity | jq -r .Account)
IS_LAMBDA_FUNCTION=$(python project.py --is-a lambda_function)
IS_LAMBDA_LAYER=$(python project.py --is-a lambda_layer)
BUILD_BUCKET="builds-${ACCOUNT_ID}"
VERSION=$(python project.py -v)

LAMBDA_FUNCTION_NAME=$(python project.py --lambda-function-name)
LAMBDA_LAYER_NAME=$(python project.py --lambda-layer-name)
PROJECT_NAME=$(python project.py --project-name)

if [ ${IS_LAMBDA_FUNCTION} == "True" ]; 
then
    echo "===== Configure lambda layers ..."
    python jenkins/configure_lambda_layers.py ${LAMBDA_FUNCTION_NAME} \
        --profile ${ENVIRONMENT_NAME}

    echo "===== Deploying lambda function ..."
    aws --profile ${ENVIRONMENT_NAME} s3 cp ${PROJECT_NAME}.zip \
        s3://${BUILD_BUCKET}/lambda/${PROJECT_NAME}/${PROJECT_NAME}-${VERSION}.zip

    AWS_VERSION=$(aws --profile ${ENVIRONMENT_NAME} lambda update-function-code \
        --publish \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --s3-bucket ${BUILD_BUCKET} \
        --s3-key lambda/${PROJECT_NAME}/${PROJECT_NAME}-${VERSION}.zip \
        --region us-east-1 | jq -r .Version)

    aws --profile ${ENVIRONMENT_NAME} lambda create-alias \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --name $(echo ${VERSION} | tr '.' '_') \
        --function-version ${AWS_VERSION}

    aws --profile ${ENVIRONMENT_NAME} lambda update-alias \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --name current \
        --function-version ${AWS_VERSION}
fi

if [ ${IS_LAMBDA_LAYER} == "True" ]; 
then
    echo "===== Deploying lambda layer ..."
    aws --profile ${ENVIRONMENT_NAME} lambda publish-layer-version \
        --layer-name $(python project.py --lambda-layer-name) \
        --description ${VERSION} \
        --compatible-runtimes python3.8 \
        --zip-file fileb://layer.zip
fi
