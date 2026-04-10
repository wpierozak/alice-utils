"""
LHC Period Statistics API Module

Fetches and processes LHC period statistics from the AliBookkeeping API.
"""
from __future__ import annotations

import logging

from modules.base import AliBookkeepingBase

# Configure module-level logger
logger = logging.getLogger(__name__)


class LHCPeriodStatisticsAPI(AliBookkeepingBase):
    """
    Client for fetching LHC Period Statistics from the AliBookkeeping API.

    Inherits token handling, HTTP helpers, and JSON save from AliBookkeepingBase.
    """

    def __init__(self, token: str = None) -> None:
        super().__init__(token)
        self._period_cache: dict[str, int] = {}

    def fetch_all(self, limit: int = 1000) -> list[dict]:
        """
        Fetches all LHC period statistics from the API with pagination support.

        Args:
            limit (int): Maximum number of records per page (default: 1000).

        Returns:
            list[dict]: A list of period statistics entries.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/lhcPeriodsStatistics"
        all_data = []
        offset = 0

        logger.info("Fetching all LHC period statistics from API...")
        while True:
            params = {"page[offset]": offset, "page[limit]": limit}

            logger.debug(f"Requesting period statistics with offset {offset} and limit {limit}...")
            response = self._get(url, params)

            data = response.json().get("data", [])
            if not data:
                break

            all_data.extend(data)
            offset += limit

            if len(data) < limit:
                break

        logger.info(f"Retrieved {len(all_data)} period statistics entries.")
        return all_data

    def get_period_names(self) -> list[str]:
        """
        Retrieves a sorted list of all available LHC period names.

        Also populates the internal period-ID cache as a side effect.

        Returns:
            list[str]: A list of period names sorted alphabetically.
        """
        data = self.fetch_all()
        names = []
        for item in data:
            lp = item.get("lhcPeriod", {})
            name = lp.get("name")
            pid = lp.get("id")
            if name:
                names.append(name)
                if pid is not None:
                    self._period_cache[name] = pid
        return sorted(names)

    def get_period_id(self, period_name: str) -> int:
        """
        Retrieves the internal ID for a given LHC period name (e.g., 'LHC25aj').

        This method caches results to minimize redundant API calls.

        Args:
            period_name (str): The name of the LHC period.

        Returns:
            int: The ``lhcPeriodId`` corresponding to the given period name.

        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the period name cannot be found in the API response.
        """
        if period_name in self._period_cache:
            logger.debug(f"Period '{period_name}' found in cache (ID: {self._period_cache[period_name]}).")
            return self._period_cache[period_name]

        logger.info(f"Fetching LHC period ID for '{period_name}' from API...")
        data = self.fetch_all()
        for item in data:
            lp = item.get("lhcPeriod", {})
            if lp.get("name") == period_name:
                pid = lp.get("id")
                if pid is not None:
                    self._period_cache[period_name] = pid
                    logger.debug(f"Successfully mapped '{period_name}' to ID {pid}.")
                    return pid

        logger.error(f"Failed to find period '{period_name}' in API response.")
        raise ValueError(f"Period '{period_name}' not found.")

    def get_statistics_for_period(self, period_name: str) -> dict | None:
        """
        Retrieves full statistics for a specific LHC period by name.

        Args:
            period_name (str): The name of the LHC period (e.g., 'LHC25aj').

        Returns:
            dict | None: The statistics entry for the requested period, or None if not found.
        """
        data = self.fetch_all()
        for item in data:
            if item.get("lhcPeriod", {}).get("name") == period_name:
                logger.info(f"Found statistics for period '{period_name}'.")
                return item
        logger.warning(f"Period '{period_name}' not found in statistics.")
        return None
