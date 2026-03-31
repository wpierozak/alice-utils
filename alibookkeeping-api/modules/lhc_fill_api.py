import os
import json
import logging
import requests
import urllib3

# Suppress insecure request warnings as the API requires verify=False for CERN certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure module-level logger
logger = logging.getLogger(__name__)

class LHCFillAPI:
    """
    Client for fetching LHC Fill data from the AliBookkeeping API.
    """

    def __init__(self, token: str = None) -> None:
        """
        Initializes the LHC Fill API client.

        Args:
            token (str, optional): The JWT token to authenticate with the API.
                                   If not provided, reads from the `ALIBK_API_TOKEN`
                                   environment variable.
        """
        self.token = token or os.environ.get("ALIBK_API_TOKEN")
        if not self.token:
            logger.error("No API token provided or found in ALIBK_API_TOKEN.")
            raise ValueError("API token is required. Pass it directly or set ALIBK_API_TOKEN environment variable.")
        
        self.base_url = "https://ali-bookkeeping.cern.ch/api"
        logger.debug("LHCFillAPI instantiated successfully.")

    def get_fill_data(self, fill_number: int) -> dict:
        """
        Retrieves data for a specific LHC fill number.

        Args:
            fill_number (int): The LHC fill number to retrieve.

        Returns:
            dict: The JSON response containing the fill details.
        """
        logger.info(f"Fetching data for LHC fill {fill_number} from API...")
        url = f"{self.base_url}/lhcFills/{fill_number}"
        params = {"token": self.token}
        
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        
        return response.json()

    def save_fill_data(self, fill_number: int, output_file: str) -> None:
        """
        Fetches the LHC fill data and saves it to a JSON file.

        Args:
            fill_number (int): The LHC fill number to retrieve.
            output_file (str): The destination JSON file path.
        """
        data = self.get_fill_data(fill_number)
        logger.info(f"Dumping fill data to JSON file '{output_file}'...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Dump complete.")
