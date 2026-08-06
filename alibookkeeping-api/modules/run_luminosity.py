"""Fetch and calculate per-run luminosity values from AliBookkeeping."""
from __future__ import annotations

import csv
import logging
import math
from collections.abc import Iterable

from modules.base import AliBookkeepingBase

logger = logging.getLogger(__name__)


class RunLuminosityAPI(AliBookkeepingBase):
    """AliBookkeeping client and CSV exporter for run luminosity values."""

    PROTON_PROTON = "pp"
    LEAD_LEAD = "PbPb"
    PP_COUNTER_CLASS = "CMTVX-NONE-NOPF-CRU"
    PBPB_COUNTER_CLASS = "C1ZNC-B-NOPF-CRU"
    REVOLUTION_FREQUENCY_HZ = 11245

    CSV_FIELDS = (
        "runNumber",
        "integratedLuminosityUbInv",
        "triggerRateHz",
        "pileUpVisible",
        "crossSectionUb",
        "triggerEfficiency",
        "triggerAcceptance",
    )

    def fetch_run(self, run_number: int) -> dict:
        """Fetch the full metadata object for one run."""
        response = self._get(f"{self.base_url}/runs/{run_number}")
        return response.json().get("data", {})

    def fetch_ctp_trigger_counters(self, run_number: int) -> list[dict]:
        """Fetch all CTP trigger counters for one run."""
        response = self._get(f"{self.base_url}/ctp-trigger-counters/{run_number}")
        return response.json().get("data", [])

    @staticmethod
    def _number(value: object) -> float | None:
        if value is None or isinstance(value, bool):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    @classmethod
    def calculate(cls, run: dict, ctp_trigger_counters: Iterable[dict]) -> dict:
        """Calculate the values displayed by the Bookkeeping run details page."""
        beam_type = run.get("pdpBeamType")
        counter_class = None
        counter_field = None
        if beam_type == cls.PROTON_PROTON:
            counter_class, counter_field = cls.PP_COUNTER_CLASS, "lmb"
        elif beam_type == cls.LEAD_LEAD:
            counter_class, counter_field = cls.PBPB_COUNTER_CLASS, "l1a"

        counter = next(
            (item for item in ctp_trigger_counters if item.get("className") == counter_class),
            None,
        )
        triggers = cls._number(counter.get(counter_field)) if counter and counter_field else None
        duration_ms = cls._number(run.get("runDuration"))
        trigger_rate = 1000 * triggers / duration_ms if triggers is not None and duration_ms else None

        lhc_fill = run.get("lhcFill") or {}
        bunch_count = cls._number(lhc_fill.get("collidingBunchesCount"))
        pile_up = None
        if trigger_rate is not None and bunch_count:
            logarithm_argument = 1 - trigger_rate / (cls.REVOLUTION_FREQUENCY_HZ * bunch_count)
            if logarithm_argument > 0:
                pile_up = -math.log(logarithm_argument)

        cross_section = cls._number(run.get("crossSection"))
        efficiency = cls._number(run.get("triggerEfficiency"))
        acceptance = cls._number(run.get("triggerAcceptance"))
        integrated_luminosity = None
        if triggers is not None and cross_section and efficiency and acceptance and pile_up:
            integrated_luminosity = (
                triggers / (cross_section * efficiency * acceptance)
                * pile_up / (1 - math.exp(-pile_up))
            )

        return {
            "runNumber": run.get("runNumber"),
            "integratedLuminosityUbInv": integrated_luminosity,
            "triggerRateHz": trigger_rate,
            "pileUpVisible": pile_up,
            "crossSectionUb": cross_section,
            "triggerEfficiency": efficiency,
            "triggerAcceptance": acceptance,
        }

    def fetch_luminosity(self, run_number: int) -> dict:
        """Fetch the inputs and calculate luminosity values for one run."""
        logger.info("Fetching luminosity inputs for run %s", run_number)
        run = self.fetch_run(run_number)
        counters = self.fetch_ctp_trigger_counters(run_number)
        values = self.calculate(run, counters)
        # A valid API response should contain this, but retain the requested run
        # number so an incomplete response still creates an identifiable row.
        values["runNumber"] = values["runNumber"] or run_number
        return values

    def export_csv(self, run_numbers: Iterable[int], output_file: str) -> list[dict]:
        """Fetch luminosity values for the supplied runs and write a CSV file."""
        rows = [self.fetch_luminosity(int(run_number)) for run_number in run_numbers]
        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.CSV_FIELDS, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        logger.info("Wrote %s luminosity rows to %s", len(rows), output_file)
        return rows
