"""
AliBookkeeping API Base Module

Shared base class for all AliBookkeeping API clients, providing common
token handling, HTTP request logic, and JSON serialization utilities.
"""
from __future__ import annotations

import os
import json
import logging

import requests
import urllib3

# Suppress insecure request warnings as the API requires verify=False for CERN certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure module-level logger
logger = logging.getLogger(__name__)


class AliBookkeepingBase:
    """
    Base class for AliBookkeeping API clients.

    Centralizes token resolution, base URL, HTTP helpers, and JSON save logic
    so that individual endpoint modules don't duplicate this boilerplate.

    Attributes:
        base_url (str): The base URL for the AliBookkeeping API.
        token (str): JWT authentication token.
    """

    BASE_URL = "https://ali-bookkeeping.cern.ch/api"

    def __init__(self, token: str = None) -> None:
        """
        Initializes the base API client.

        Args:
            token (str, optional): The JWT token to authenticate with the API.
                                   If not provided, reads from the `ALIBK_API_TOKEN`
                                   environment variable.

        Raises:
            ValueError: If no token is provided or found in the environment variables.
        """
        self.token = token or os.environ.get("ALIBK_API_TOKEN")
        if not self.token:
            logger.error("No API token provided or found in ALIBK_API_TOKEN.")
            raise ValueError(
                "API token is required. Pass it directly or set ALIBK_API_TOKEN environment variable."
            )
        self.base_url = self.BASE_URL
        logger.debug(f"{self.__class__.__name__} instantiated successfully.")

    def _get(self, url: str, params: dict = None) -> requests.Response:
        """
        Performs a GET request with the API token and SSL verification disabled.

        Args:
            url (str): The full URL to request.
            params (dict, optional): Query parameters (token is added automatically).

        Returns:
            requests.Response: The response object (already checked for HTTP errors).

        Raises:
            requests.HTTPError: If the API returns a non-2xx status code.
        """
        if params is None:
            params = {}
        params.setdefault("token", self.token)

        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        return response

    def save_to_json(self, data: list | dict, output_file: str) -> None:
        """
        Saves data to a JSON file.

        Args:
            data (list | dict): The data to save.
            output_file (str): The destination file path.
        """
        logger.info(f"Dumping data to JSON file '{output_file}'...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Dump complete.")
