from __future__ import print_function

import argparse
import json

import boto3

parser = argparse.ArgumentParser()
parser.add_argument('function_name')
parser.add_argument('--profile', '-p', default='default')

args = parser.parse_args()

function_name = args.function_name
profile = args.profile

session = boto3.Session(profile_name=profile)
lambda_cli = session.client('lambda')
layers = json.load(open('project.json')).get('layers')
arns = []

for layer, version in layers.items():
    print('Searching for', layer, version)
    available_versions = lambda_cli.list_layer_versions(LayerName=layer)
    filtered = [v for v in available_versions['LayerVersions']
                if v.get('Description') == version]

    if filtered:
        arn = filtered[0]['LayerVersionArn']
        arns.append(arn)
        print('Found arn', arn)

if arns:
    print('Updating function configuration')
    lambda_cli.update_function_configuration(FunctionName=function_name,
                                             Layers=arns)
