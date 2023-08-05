import os
import pytest
import boto3
from moto import (
    mock_ssm,
    mock_secretsmanager
)

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# create a boto3 session using moto
@pytest.fixture(scope='function')
def boto3_session(aws_credentials):
    with mock_ssm():
        yield boto3.Session(region_name='us-east-1')

@pytest.fixture(scope='function')
def ssm(aws_credentials):
    with mock_ssm():
        yield boto3.client('ssm', region_name='us-east-1')

@pytest.fixture
def test_param():
    parameter_path = '/path/to/parameter'
    parameter_value = 'expected_value'
    return parameter_path, parameter_value

@pytest.fixture(scope='function')
def secretsmanager(aws_credentials):
    with mock_secretsmanager():
        yield boto3.client('secretsmanager', region_name='us-east-1')

# test secret
@pytest.fixture
def test_secret():
    secret_path = '/path/to/secret'
    secret_value = '********'
    return secret_path, secret_value
