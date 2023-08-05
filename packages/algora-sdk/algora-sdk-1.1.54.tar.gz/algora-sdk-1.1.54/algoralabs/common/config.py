"""
Module containing configuration classes used for configuring the algoralabs sdk
"""
import os
from typing import Optional, Dict

from algoralabs.decorators.configuration import configuration
from algoralabs.gData import config_file


@configuration
class Auth:
    """
    Configuration class for getting the authentication information from the environment
    """
    # Feature to keep values hidden from printing (not totally)
    # Allows for dynamic rendering of auth values
    @property
    def username(self) -> Optional[str]:
        return os.getenv("ALGORA_USER", None)

    @property
    def password(self) -> Optional[str]:
        return os.getenv("ALGORA_PWD", None)

    @property
    def token(self) -> Optional[str]:
        return os.getenv("AUTH_TOKEN", None)

    def can_authenticate(self) -> bool:
        """
        Tests the environment to see if the user provided enough info to authenticate requests

        Returns:
            A boolean that represents whether you can authenticate requests
        """
        auth_options = self.token or (self.username and self.password)
        return auth_options is not None

    def __eq__(self, other: "Auth"):
        return (
            self.token == other.token and
            self.username == self.username and
            self.password == self.password
        )


@configuration(yaml_file=config_file, prefix="")
class AppConfig:
    """
    Configuration class for getting app information
    """
    app_name: str
    environment: str
    version: str


app_config = AppConfig()


@configuration(yaml_file=config_file, prefix=app_config.environment)
class EnvironmentConfig:
    """
    Configuration class for getting environment information
    """
    urls: dict
    auth_config: Auth = Auth()

    def get_url(self, key: str = "algora") -> str:
        return self.urls.get(key, self.urls["algora"])

