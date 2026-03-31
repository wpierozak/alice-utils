"""
AliBookkeeping API Framework

A lightweight Python wrapper to retrieve LHC periods and runs from the ALICE
bookkeeping API at CERN.
"""

import os
import json
import logging

import requests
import urllib3

# Suppress insecure request warnings as the API requires verify=False for CERN certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure module-level logger
logger = logging.getLogger(__name__)

class AliBookkeepingAPI:
    """
    Client for the AliBookkeeping API exposing methods to query LHC periods and runs.
    
    Attributes:
        base_url (str): The base URL for the AliBookkeeping API.
        token (str): JWT authentication token.
    """

    def __init__(self, token: str = None) -> None:
        """
        Initializes the AliBookkeeping API client.

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
            raise ValueError("API token is required. Pass it directly or set ALIBK_API_TOKEN environment variable.")
        
        self.base_url = "https://ali-bookkeeping.cern.ch/api"
        self._period_cache: dict[str, int] = {}
        logger.debug("AliBookkeepingAPI instantiated successfully.")

    def get_period_id(self, period_name: str) -> int:
        """
        Retrieves the internal ID for a given LHC period name (e.g., 'LHC25aj').
        
        This method caches the results to minimize redundant API calls.

        Args:
            period_name (str): The name of the LHC period.

        Returns:
            int: The `lhcPeriodId` corresponding to the given period name.
            
        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the period name cannot be found in the API response.
        """
        if period_name in self._period_cache:
            logger.debug(f"Period '{period_name}' found in cache (ID: {self._period_cache[period_name]}).")
            return self._period_cache[period_name]

        logger.info(f"Fetching LHC period ID for '{period_name}' from API...")
        url = f"{self.base_url}/lhcPeriodsStatistics"
        params = {"page[offset]": 0, "page[limit]": 1000, "token": self.token}
        
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        
        data = response.json().get("data", [])
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

    def get_period_names(self) -> list[str]:
        """
        Retrieves a list of all available LHC period names.

        Returns:
            list[str]: A list of period names.
            
        Raises:
            requests.HTTPError: If the API request fails.
        """
        logger.info("Fetching all LHC period names from API...")
        url = f"{self.base_url}/lhcPeriodsStatistics"
        params = {"page[offset]": 0, "page[limit]": 1000, "token": self.token}
        
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        
        data = response.json().get("data", [])
        period_names = []
        for item in data:
            lp = item.get("lhcPeriod", {})
            name = lp.get("name")
            pid = lp.get("id")
            if name:
                period_names.append(name)
                if pid is not None:
                    self._period_cache[name] = pid
                    
        logger.info(f"Retrieved {len(period_names)} period names.")
        return period_names

    def fetch_runs(
        self, 
        period_name: str, 
        include_tag: str = None, 
        exclude_tag: str = None, 
        run_qualities: str = "good", 
        definitions: str = "PHYSICS"
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
                "token": self.token
            }
            if run_qualities:
                params["filter[runQualities]"] = run_qualities
            if definitions:
                params["filter[definitions]"] = definitions

            logger.debug(f"Requesting runs with offset {offset} and limit {limit}...")
            response = requests.get(url, params=params, verify=False)
            response.raise_for_status()
            
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

    def dump_to_json(self, data: list | dict, filename: str) -> None:
        """
        Dumps raw data (such as the list of runs) to a JSON file.

        Args:
            data (list | dict): The raw data to dump.
            filename (str): The destination file path.
        """
        logger.info(f"Dumping data to JSON file '{filename}'...")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Dump complete.")
