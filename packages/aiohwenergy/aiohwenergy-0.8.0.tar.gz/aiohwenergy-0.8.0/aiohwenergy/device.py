"""Device represents basic information about the product."""

import logging
from typing import Coroutine

_LOGGER = logging.getLogger(__name__)


class Device:
    """Represent Device config."""

    def __init__(self, request: Coroutine) -> None:
        """Initialize new Device object."""
        self._request = request
        self._raw = None

    def __eq__(self, other: object) -> bool:
        """Return true when other object is equal to this object."""
        if other is None:
            return False
        return self._raw == other._raw

    def todict(self) -> dict:
        return self._raw

    @property
    def product_name(self) -> str:
        """Friendly name of the device."""
        return self._raw["product_name"]

    @property
    def product_type(self) -> str:
        """Device Type identifier."""
        return self._raw["product_type"]

    @property
    def serial(self) -> str:
        """
        Return readable serial id.

        Formatted as hex string of the 12 characters without delimiters
        eg: "aabbccddeeff"
        """
        return self._raw["serial"]

    @property
    def api_version(self) -> str:
        """Return API version of the device."""
        return self._raw["api_version"]

    @property
    def firmware_version(self) -> str:
        """
        User readable version of the device firmware.

        Formatted as %d%02d e.g. 2.03
        """
        return self._raw["firmware_version"]

    async def update(self) -> bool:
        """Fetch new data for device."""
        response = await self._request("get", "api")
        if response is None:
            return False

        self._raw = response
        return True
