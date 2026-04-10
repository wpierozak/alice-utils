"""
AliBookkeeping API Framework

A lightweight Python wrapper to retrieve LHC periods and runs from the ALICE
bookkeeping API at CERN.
"""
from __future__ import annotations

import logging

from modules.base import AliBookkeepingBase
from modules.lhc_period_statistics import LHCPeriodStatisticsAPI

# Configure module-level logger
logger = logging.getLogger(__name__)


class AliBookkeepingAPI(AliBookkeepingBase):
    """
    Client for the AliBookkeeping API exposing methods to query runs.

    Period name → ID resolution is delegated to LHCPeriodStatisticsAPI.
    Inherits token handling, HTTP helpers, and JSON save from AliBookkeepingBase.
    """

    def __init__(self, token: str = None) -> None:
        super().__init__(token)
        self._period_stats = LHCPeriodStatisticsAPI(token=self.token)

    def get_period_id(self, period_name: str) -> int:
        """
        Retrieves the internal ID for a given LHC period name (e.g., 'LHC25aj').

        Delegates to LHCPeriodStatisticsAPI which caches results.

        Args:
            period_name (str): The name of the LHC period.

        Returns:
            int: The ``lhcPeriodId`` corresponding to the given period name.

        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the period name cannot be found in the API response.
        """
        return self._period_stats.get_period_id(period_name)

    def fetch_runs(
        self,
        period_name: str,
        include_tag: str = None,
        exclude_tag: str = None,
        run_qualities: str = "good",
        definitions: str = "PHYSICS",
    ) -> list[dict]:
        """
        Fetches a list of runs belonging to a specific LHC period, with optional filtering.

        Args:
            period_name (str): The LHC period name (e.g., 'LHC25aj').
            include_tag (str, optional): If provided, only returns runs containing this tag.
            exclude_tag (str, optional): If provided, excludes any runs containing this tag.
            run_qualities (str): Filter by run qualities (default is "good").
            definitions (str): Filter by definitions (default is "PHYSICS").

        Returns:
            list[dict]: A list of dictionaries, each representing a run's metadata.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        period_id = self.get_period_id(period_name)

        url = f"{self.base_url}/runs"
        all_runs = []
        offset = 0
        limit = 100

        logger.info(f"Fetching runs for period '{period_name}' (ID: {period_id})...")
        while True:
            params = {
                "page[offset]": offset,
                "page[limit]": limit,
                "filter[lhcPeriodIds][]": period_id,
            }
            if run_qualities:
                params["filter[runQualities]"] = run_qualities
            if definitions:
                params["filter[definitions]"] = definitions

            logger.debug(f"Requesting runs with offset {offset} and limit {limit}...")
            response = self._get(url, params)

            data = response.json().get("data", [])
            if not data:
                break

            all_runs.extend(data)
            offset += limit

            if len(data) < limit:
                break

        logger.info(f"Retrieved {len(all_runs)} total runs from API before local tag filtering.")

        # Local tag filtering
        if include_tag or exclude_tag:
            filtered_runs = []
            for run in all_runs:
                run_tags = [t.get("text", "") for t in run.get("tags", [])]

                if include_tag and include_tag not in run_tags:
                    continue

                if exclude_tag and exclude_tag in run_tags:
                    continue

                filtered_runs.append(run)

            logger.info(f"Filtered runs from {len(all_runs)} to {len(filtered_runs)} based on tags.")
            return filtered_runs

        return all_runs
