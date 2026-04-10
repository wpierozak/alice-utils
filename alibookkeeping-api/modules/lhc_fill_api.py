"""
LHC Fill API Module

Fetches LHC Fill data from the AliBookkeeping API.
"""
from __future__ import annotations

import logging

from modules.base import AliBookkeepingBase

# Configure module-level logger
logger = logging.getLogger(__name__)


class LHCFillAPI(AliBookkeepingBase):
    """
    Client for fetching LHC Fill data from the AliBookkeeping API.

    Inherits token handling, HTTP helpers, and JSON save from AliBookkeepingBase.
    """

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
        response = self._get(url)
        return response.json()

    def save_fill_data(self, fill_number: int, output_file: str) -> None:
        """
        Fetches the LHC fill data and saves it to a JSON file.

        Args:
            fill_number (int): The LHC fill number to retrieve.
            output_file (str): The destination JSON file path.
        """
        data = self.get_fill_data(fill_number)
        self.save_to_json(data, output_file)
