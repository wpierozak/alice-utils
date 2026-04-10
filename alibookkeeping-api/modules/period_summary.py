"""
Period Summary API Module

Fetches period summary data (including QC flags) from the AliBookkeeping API
for a given LHC period.
"""
from __future__ import annotations

import logging

from modules.base import AliBookkeepingBase
from modules.lhc_period_statistics import LHCPeriodStatisticsAPI

# Configure module-level logger
logger = logging.getLogger(__name__)


class PeriodSummaryAPI(AliBookkeepingBase):
    """
    Client for fetching Period Summary from the AliBookkeeping API.

    Inherits token handling, HTTP helpers, and JSON save from AliBookkeepingBase.
    """

    def __init__(self, token: str = None) -> None:
        super().__init__(token)
        self._period_stats = LHCPeriodStatisticsAPI(token=self.token)

    def fetch_summary(self, lhc_period_id: int) -> dict:
        """
        Fetches the period summary for a given LHC period ID.

        Args:
            lhc_period_id (int): The internal numeric ID of the LHC period.

        Returns:
            dict: The JSON response containing the period summary.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        logger.info(f"Fetching period summary for period ID {lhc_period_id}...")
        url = f"{self.base_url}/qcFlags/summary"
        params = {"lhcPeriodId": lhc_period_id}
        response = self._get(url, params)
        return response.json()

    def fetch_summary_by_name(self, period_name: str) -> dict:
        """
        Fetches the period summary for a given LHC period name.

        Resolves the period name to its numeric ID via LHCPeriodStatisticsAPI,
        then fetches the summary.

        Args:
            period_name (str): The LHC period name (e.g., 'LHC25aj').

        Returns:
            dict: The JSON response containing the period summary.

        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the period name cannot be resolved to an ID.
        """
        period_id = self._period_stats.get_period_id(period_name)
        logger.info(f"Resolved period '{period_name}' to ID {period_id}.")
        return self.fetch_summary(period_id)
