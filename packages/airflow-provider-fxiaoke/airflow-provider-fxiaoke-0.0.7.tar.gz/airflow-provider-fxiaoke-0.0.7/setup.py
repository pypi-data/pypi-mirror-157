from setuptools import find_packages, setup

from airflow_fxiaoke import get_provider_info

with open("README.md", "r") as fh:
    long_description = fh.read()

provider = get_provider_info()

"""Perform the package airflow-provider-fxiaoke setup."""
setup(
    name=provider['package-name'],
    version=provider['versions'][0],
    description=provider['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        "apache_airflow_provider": [
            "provider_info=airflow_fxiaoke.__init__:get_provider_info"
        ]
    },
    license='Apache License 2.0',
    packages=find_packages(include=[
        'airflow_fxiaoke',
        'airflow_fxiaoke.hooks',
        'airflow_fxiaoke.operators'
    ]),
    package_data={'airflow_fxiaoke': ['./provider.yaml',]},
    install_requires=provider['additional-dependencies'],
    setup_requires=['setuptools', 'wheel'],
    author='wbin',
    author_email='wbin.chn@gmail.com',
    url='https://github.com/wbchn/apache-airflow-providers-fxiaoke',
    classifiers=[
        "Framework :: Apache Airflow",
        "Framework :: Apache Airflow :: Provider",
    ],
    keywords=['clickhouse', 'airflow', 'providers', 'fxiaoke', 'ShareCRM'],
    python_requires='~=3.8',
)
