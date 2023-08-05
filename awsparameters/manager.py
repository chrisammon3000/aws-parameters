import logging
from typing import Union, Tuple
from dataclasses import dataclass
from functools import lru_cache
import re
import json
from typing import Any
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@lru_cache
def get_parameter_value(ssm_client, parameter_path: str) -> str:
    logger.info(f"Retrieving parameter {parameter_path}")
    return ssm_client.get_parameter(Name=parameter_path)["Parameter"]["Value"]


@lru_cache
def get_secret_value(secretsmanager_client, secret_id: str) -> str:
    logger.info(f"Retrieving secret {secret_id}")
    return secretsmanager_client.get_secret_value(SecretId=secret_id)[
        "SecretString"
    ]


@dataclass
class JsonModel:
    __slots__ = "__dict__"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return json.dumps(self.__dict__)

    def __repr__(self) -> str:
        return self.__dict__()

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class SessionManager:
    def __init__(
        self, boto3_session=None, region_name: str = None, **kwargs
    ) -> None:
        self.session = boto3_session or boto3.Session(region_name=region_name)
        self.clients = {}  # Cache for clients
        self.resources = {}  # Cache for resources
        self._init_clients_or_resources(**kwargs)

    def _init_clients_or_resources(self, **kwargs):
        """Initializes clients and resources from the boto3 session when created"""

        if "get_clients" in kwargs:
            for service in kwargs["get_clients"]:
                self.get_client(service)
        if "get_resources" in kwargs:
            for service in kwargs["get_resources"]:
                self.get_resource(service)

    def get_client(self, service_name: str):
        if service_name not in self.clients:
            self.clients[service_name] = self.session.client(service_name)
        return self.clients[service_name]

    def get_resource(self, service_name: str):
        if service_name not in self.resources:
            self.resources[service_name] = self.session.resource(service_name)
        return self.resources[service_name]

    def __getattr__(self, name):
        return getattr(self.session, name)


class ConfigManager(JsonModel):
    def __init__(self, **kwargs) -> None:
        self._service = kwargs["service"]
        self._attr_map = kwargs["attr_map"]
        self._client = kwargs["client"]

        for name in self._attr_map.keys():
            setattr(
                self, f"_{name}", None
            )  # storing initial None values in "_name" attributes
            getter = self.make_getter(name)
            setattr(
                self.__class__, name, property(getter)
            )  # create properties for each attribute

    def make_getter(self, name):
        def getter(instance):
            if (
                instance.__dict__[f"_{name}"] is None
            ):  # check if the corresponding "_name" attribute is None
                if instance._service == "ssm":
                    value = get_parameter_value(
                        instance._client, instance._attr_map[name]
                    )
                elif instance._service == "secretsmanager":
                    value = get_secret_value(
                        instance._client, instance._attr_map[name]
                    )
                else:
                    raise ValueError(
                        f"Service {instance._service} not supported, must be"
                        " one of 'ssm' or 'secretsmanager'"
                    )

                # detect json
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

                instance.__dict__[f"_{name}"] = (
                    value  # store the value in "_name" attribute
                )
            return instance.__dict__[f"_{name}"]

        return getter

    def list(self):
        return list(self._attr_map.values())

    def __str__(self) -> str:
        return json.dumps(
            {
                k: v
                for k, v in self.__dict__.items()
                if not k.startswith("_") and k != "client"
            }
        )

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class ParamsConfigManager(ConfigManager):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class SecretsConfigManager(ConfigManager):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


# TODO support for retrieving all params under a path (this circumvents the need for deploying a mapping parameter)
# TODO support for loading param mappings from a file
# TODO create a ConfigBuilder to build the param mappings from already available parameters stored in SSM/SecretsManager using a path
# TODO integrate LambdaPowerTools as an optional dependency
# TODO add json() method
class AppConfig:
    """Class to manage the configuration of the application using SSM Parameter Store and Secrets Manager.

    Usage:
        >>> config = AppConfig(ssm_mapping=ssm_mapping, secrets_mapping=secrets_mapping)
        >>> # Show application environment variables
        >>> config.env
        >>> # Fetch a parameter
        >>> config.pipeline.github_source_repository
        >>> # Fetch a secret
        >>> config.database.neo4j_credentials

    Args:
        ssm_mapping (dict, optional): Mapping of parameter names to their path in SSM Parameter Store. Defaults to None.
        secrets_mapping (dict, optional): Mapping of secret names to their path in Secrets Manager. Defaults to None.
        boto3_session ([type], optional): Boto3 session to use. Defaults to None.
    """

    def __init__(
        self,
        mappings_path: str = None,
        path_separator: str = "/",
        boto3_session=None,
        region_name: str = None,
    ) -> None:
        self.mappings_path = mappings_path
        self.path_separator = path_separator
        self.session = SessionManager(
            boto3_session,
            region_name,
            get_clients=["ssm"] if mappings_path else [],
        )
        self.ssm_paths, self.secrets_paths = (
            self._load_service_mappings() if mappings_path else None
        )
        self.services, self._attr_map = self._build_attr_mappings()
        for service in self.services:
            if service not in self.session.clients:
                self.session.get_client(service)
            if service == "ssm":
                attr = "params"
                _cls = ParamsConfigManager
            elif service == "secretsmanager":
                attr = "secrets"
                _cls = SecretsConfigManager
            setattr(
                self,
                attr,
                _cls(
                    service=service,
                    attr_map=self._attr_map[service],
                    client=self.session.clients[service],
                ),
            )

    def _load_service_mappings(self) -> Tuple[dict, dict]:
        service_mappings = json.loads(
            self.session.clients["ssm"].get_parameter(Name=self.mappings_path)[
                "Parameter"
            ]["Value"]
        )
        return service_mappings.get("ssm", None), service_mappings.get(
            "secretsmanager", None
        )

    def _build_attr_mappings(self):
        collections = {
            k: v
            for k, v in {
                "ssm": self.ssm_paths,
                "secretsmanager": self.secrets_paths,
            }.items()
            if v is not None
        }
        services = list(collections.keys())
        mappings = {}
        for name, mapping in collections.items():
            mappings[name] = {
                item.split(self.path_separator)[-1]: item for item in mapping
            }
        return services, mappings

    @property
    def map(self):
        return self._attr_map
