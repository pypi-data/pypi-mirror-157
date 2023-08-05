import os
import yaml


def get_provider_info():
    basedir = os.path.abspath(os.path.dirname(__file__))
    provider_yaml_path = f'{basedir}/provider.yaml'
    with open(provider_yaml_path) as yaml_file:
        provider = yaml.safe_load(yaml_file)
    return provider
