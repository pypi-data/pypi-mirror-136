import io
import os

from setuptools import find_namespace_packages, setup

VERSION = '0.1.0a'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with io.open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sqlalchemy-es',
    description=('SQLAlchemy dialect for Elasticsearch with write operations support'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=VERSION,
    packages=find_namespace_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'sqlalchemy.dialects': [
            'es = sqlalchemy_dialects.es:ES_HTTP_DIALECT',
            'es.http = sqlalchemy_dialects.es:ES_HTTP_DIALECT',
            'es.https = sqlalchemy_dialects.es:ES_HTTP_DIALECT',
            'es.aws = sqlalchemy_dialects.es.aws:ES_AWS_HTTP_DIALECT',
            'es.aws.http = sqlalchemy_dialects.es.aws:ES_AWS_HTTP_DIALECT',
            'es.aws.https = sqlalchemy_dialects.es.aws:ES_AWS_HTTP_DIALECT',
        ]
    },
    install_requires=['elasticsearch>7, <7.14', 'packaging>=21.0, <22.0', 'sqlalchemy'],
    extras_require={'opendistro': ['requests_aws4auth', 'boto3']},
    # author='',
    # author_email='',
    url='https://github.com/usalko',
    download_url='https://github.com/usalko/elasticsearch-es/releases/tag/'
    + VERSION,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    tests_require=['nose>=1.0'],
    test_suite='nose.collector',
)
