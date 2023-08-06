"""
Data represents measurement data for this device.

It contains wifi strength and energy/gas data
"""
from __future__ import annotations

from datetime import datetime
from typing import Coroutine

available_attributes = [
    "available_datapoints",
    "smr_version",
    "meter_model",
    "wifi_ssid",
    "wifi_strength",
    "total_power_import_t1_kwh",
    "total_power_import_t2_kwh",
    "total_power_export_t1_kwh",
    "total_power_export_t2_kwh",
    "active_power_w",
    "active_power_l1_w",
    "active_power_l2_w",
    "active_power_l3_w",
    "total_gas_m3",
    "gas_timestamp",
]


class Data:
    """Represent Device config."""

    def __init__(self, request: Coroutine) -> None:
        """Initialize new Data object."""
        self._raw = None
        self._request = request
        self.available_datapoints = []

    def __eq__(self, other: object) -> bool:
        """Return true when other object is equal to this object."""
        if other is None:
            return False
        return self._raw == other._raw

    def todict(self) -> dict:
        return self._raw

    @property
    def smr_version(self) -> int | None:
        """
        SMR version of P1 meter.

        Available for: HWE-P1
        """
        return self._raw["smr_version"] if "smr_version" in self._raw else None

    @property
    def meter_model(self) -> str | None:
        """
        SMR version of P1 meter.

        Available for: HWE-P1
        """
        return self._raw["meter_model"] if "meter_model" in self._raw else None

    @property
    def wifi_ssid(self) -> str | None:
        """
        Wi-fi SSID currently in use (string).

        Available for: HWE-P1, SDM230-wifi, SDM630-wifi, HWE-SKT
        """
        return self._raw["wifi_ssid"] if "wifi_ssid" in self._raw else None

    @property
    def wifi_strength(self) -> int | None:
        """
        Wifi strength in percentage (number, 0-100), where 100 is best.

        Available for: HWE-P1, SDM230-wifi, SDM630-wifi, HWE-SKT
        """
        return self._raw["wifi_strength"] if "wifi_strength" in self._raw else None

    @property
    def total_power_import_t1_kwh(self) -> float | None:
        """
        Total power import value for counter 1 (number).

        Available for: HWE-P1, SDM230-wifi, SDM630-wifi, HWE-SKT
        """
        return (
            self._raw["total_power_import_t1_kwh"]
            if "total_power_import_t1_kwh" in self._raw
            else None
        )

    @property
    def total_power_import_t2_kwh(self) -> float | None:
        """
        Total power import value for counter 2 (number).

        Available for: HWE-P1
        """
        return (
            self._raw["total_power_import_t2_kwh"]
            if "total_power_import_t2_kwh" in self._raw
            else None
        )

    @property
    def total_power_export_t1_kwh(self) -> float | None:
        """
        Total power export value for counter 1 (number).

        Available for: HWE-P1, SDM230-wifi, SDM630-wifi, HWE-SKT
        """
        return (
            self._raw["total_power_export_t1_kwh"]
            if "total_power_export_t1_kwh" in self._raw
            else None
        )

    @property
    def total_power_export_t2_kwh(self) -> float | None:
        """
        Total power export value for counter 2 (number).

        Available for: HWE-P1
        """
        return (
            self._raw["total_power_export_t2_kwh"]
            if "total_power_export_t2_kwh" in self._raw
            else None
        )

    @property
    def active_power_w(self) -> float | None:
        """
        Active consumption in watts (number).

        Available for: HWE-P1, SDM230-wifi, SDM630-wifi, HWE-SKT
        """
        return self._raw["active_power_w"] if "active_power_w" in self._raw else None

    @property
    def active_power_l1_w(self) -> float | None:
        """
        Active consumption in watts for line 1 (number).

        Available for: HWE-P1, SDM230-wifi, SDM630-wifi, HWE-SKT
        """
        return (
            self._raw["active_power_l1_w"] if "active_power_l1_w" in self._raw else None
        )

    @property
    def active_power_l2_w(self) -> float | None:
        """
        Active consumption in watts for line 2 (number).

        Note: DSMR meters are available in single and three-phase variants. P1 meter supports both
              This data value will be 'None' when P1 meter is connected to single phase meter
        Available for: HWE-P1, SDM630-wifi
        """
        return (
            self._raw["active_power_l2_w"] if "active_power_l2_w" in self._raw else None
        )

    @property
    def active_power_l3_w(self) -> float | None:
        """
        Active consumption in watts for line 3 (number).

        Note: DSMR meters are available in single and three-phase variants. P1 meter supports both
              This data value will be 'None' when P1 meter is connected to single phase meter
        Available for: HWE-P1, SDM630-wifi
        """
        return (
            self._raw["active_power_l3_w"] if "active_power_l3_w" in self._raw else None
        )

    @property
    def total_gas_m3(self) -> float | None:
        """
        Total gas usage in m3 (number).

        Note: Not all DSMR meters are connected to a gas meter, so this value can be 'None'
        Available for: HWE-P1
        """
        return self._raw["total_gas_m3"] if "total_gas_m3" in self._raw else None

    @property
    def gas_timestamp(self) -> str | None:
        """
        Latest gas timestamp (number).

        Formatted as 'YYMMDDhhmmss', formatted to ISO8601
        Note: Not all DSMR meters are connected to a gas meter, so this value can be 'None'
        Available for: HWE-P1
        """
        if "gas_timestamp" not in self._raw:
            return None

        if self._raw["gas_timestamp"] is None:
            return None

        date = datetime.strptime(str(self._raw["gas_timestamp"]), "%y%m%d%H%M%S")
        return date.isoformat()

    async def update(self) -> bool:
        """Fetch new data for object."""
        response = await self._request("get", "api/v1/data")

        if response is None:
            return False

        self._raw = response

        for datapoint in self._raw:
            if (
                datapoint not in self.available_datapoints
                and datapoint in available_attributes
            ):
                self.available_datapoints.append(datapoint)
        return True
