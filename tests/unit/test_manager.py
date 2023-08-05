import json
import pytest
from unittest.mock import Mock, patch
from tests.unit.fixtures import (
    aws_credentials,
    ssm,
    test_param,
    secretsmanager,
    test_secret,
    boto3_session
)
from awsparameters.manager import (
    get_parameter_value,
    get_secret_value,
    JsonModel,
    SessionManager,
    ConfigManager,
    AppConfig
)

def test_get_parameter_value(ssm, test_param):
    parameter_path, parameter_value = test_param

    ssm.put_parameter(
        Name=parameter_path,
        Value=parameter_value,
        Type="String",
        Overwrite=True
    )

    assert get_parameter_value(ssm, parameter_path) == parameter_value

def test_get_secret_value(secretsmanager, test_secret):
    secret_path, secret_value = test_secret

    secretsmanager.create_secret(
        Name=secret_path,
        SecretString=secret_value
    )

    assert get_secret_value(secretsmanager, secret_path) == secret_value

def test_json_model():
    test_dict = {
        "test_key_1": "test_value_1",
        "test_key_2": "test_value_2"
    }

    test_model = JsonModel(**test_dict)

    assert test_model.test_key_1 == test_dict["test_key_1"]
    assert test_model.test_key_2 == test_dict["test_key_2"]

def test_session_manager(boto3_session):
    session_manager = SessionManager(boto3_session=boto3_session)
    assert session_manager.session == boto3_session
    assert session_manager.clients == {}
    assert session_manager.resources == {}

    # test get_client
    ssm = session_manager.get_client("ssm")
    assert session_manager.clients["ssm"] == ssm

    # test get_resource
    dynamodb = session_manager.get_resource("dynamodb")
    assert session_manager.resources["dynamodb"] == dynamodb

def test_config_manager(ssm, secretsmanager, test_param, test_secret):
    test_param_path, test_param_value = test_param
    test_secret_path, test_secret_value = test_secret

    ssm.put_parameter(
        Name=test_param_path,
        Value=test_param_value,
        Type="String",
        Overwrite=True
    )

    secretsmanager.create_secret(
        Name=test_secret_path,
        SecretString=test_secret_value
    )

    test_param_config = ConfigManager(
        service="ssm",
        attr_map={
            "test_param": test_param_path
        },
        client=ssm
    )
    assert test_param_config.test_param == test_param_value

    test_secret_config = ConfigManager(
        service="secretsmanager",
        attr_map={
            "test_secret": test_secret_path
        },
        client=secretsmanager
    )
    assert test_secret_config.test_secret == test_secret_value

    # FIXME: TypeError: attribute name must be string, not 'int'
    # # test the list() method
    # assert isinstance(list(test_param_config), list)
    # assert isinstance(list(test_secret_config), list)

def test_app_config(boto3_session, ssm, secretsmanager, test_param, test_secret):
    test_param_path, test_param_value = test_param
    test_secret_path, test_secret_value = test_secret

    mappings_path = {
        "ssm": [
            test_param_path
        ],
        "secretsmanager": [
            test_secret_path
        ]
    }

    # create a parameter of mappings_path
    ssm.put_parameter(
        Name="/test/mappings_path",
        Value=json.dumps(mappings_path),
        Type="String",
        Overwrite=True
    )

    ssm.put_parameter(
        Name=test_param_path,
        Value=test_param_value,
        Type="String",
        Overwrite=True
    )

    secretsmanager.create_secret(
        Name=test_secret_path,
        SecretString=test_secret_value
    )

    test_config = AppConfig(
        mappings_path="/test/mappings_path",
        boto3_session=boto3_session,
        region_name="us-east-1"
    )

    assert test_config.session.session.region_name == "us-east-1"
    assert test_config.ssm_paths == [test_param_path]
    assert test_config.secrets_paths == [test_secret_path]
    assert test_config.services == ["ssm", "secretsmanager"]
    assert test_config._attr_map == {
        "ssm": {
            test_param_path.split("/")[-1]: test_param_path
        },
        "secretsmanager": {
            test_secret_path.split("/")[-1]: test_secret_path
        }
    }

    # path variables from test_param and test_secret should be available as attributes:
    # for example, `parameter_path = '/path/to/parameter'` <== 'parameter' is the attribute name
    # test_config.params.parameter
    # test_config.secrets.secret
    assert test_config.params.parameter == test_param_value
    assert test_config.secrets.secret == test_secret_value