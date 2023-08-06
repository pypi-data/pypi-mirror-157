"""
Credentials business logic
"""

# Enable forward definitions
from __future__ import annotations

from os import environ
from typing import Optional

from hoppr import utils
from hoppr.exceptions import HopprCredentialsError
from hoppr.types.cred_object import CredObject
from hoppr.types.credentials_file_content import (
    CredentialFileContent,
    CredentialRequiredService,
)


class Credentials:
    """
    Credentials business logic class
    """

    def __init__(self) -> None:
        self.content = None

    @staticmethod
    def load_file(file) -> Credentials:
        """
        Creates a credentials object from a file
        """
        input_dict = utils.load_file(file)
        creds = Credentials()
        creds.populate(input_dict)

        return creds

    def find_credentials(self, url=None) -> Optional[CredObject]:
        """
        Method to find credentials that match the provided URL.
        The longest matching in the authentication object should be used.
        """

        # Find the longest "url" in the auth list that is within the "url"
        matching_service = CredentialRequiredService(url="")

        if self.content:
            for service in self.content.credential_required_services:
                if service.url in url:
                    if len(service.url) > len(matching_service.url):
                        matching_service = service

        # If no match was found, return found == False
        if matching_service.url != "":
            pass_env = matching_service.pass_env
            if pass_env not in environ:
                raise HopprCredentialsError(
                    self.content,
                    url,
                    f"'{pass_env}' not found in environment variables.",
                )

            return CredObject(
                username=str(matching_service.user), password=environ[str(pass_env)]
            )

        return None

    def populate(self, input_dict):
        """
        Populates Credentials object with dictionary contents.
        """

        self.content = CredentialFileContent(**input_dict)
