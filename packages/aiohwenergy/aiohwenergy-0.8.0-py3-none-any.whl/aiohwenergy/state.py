"""State represents state of device, eg. as 'power_on'."""
from __future__ import annotations

import logging
from typing import Coroutine
from .errors import RequestError

_LOGGER = logging.getLogger(__name__)


class State:
    """Represent current state."""

    def __init__(self, request: Coroutine):
        """Initialize new State object."""
        self._raw = None
        self._request = request

    def __eq__(self, other: object) -> bool:
        """Return true when other object is equal to this object."""
        if other is None:
            return False
        return self._raw == other._raw

    def todict(self) -> dict:
        return self._raw

    async def set(
        self,
        power_on: bool | None = None,
        switch_lock: bool | None = None,
        brightness: int | None = None,
    ) -> bool:
        """Set state of device."""
        state = {}

        if power_on is not None:
            state["power_on"] = power_on
        if switch_lock is not None:
            state["switch_lock"] = switch_lock
        if brightness is not None:
            state["brightness"] = brightness

        if state == {}:
            _LOGGER.error("At least one state update is required")
            return False

        try:
            response = await self._request("put", "api/v1/state", state)
            if response is not None:
                # Zip result and original
                self._raw = {**self._raw, **response}
                return True

        except RequestError:
            _LOGGER.error("Failed to set state")
            return False

    @property
    def power_on(self) -> bool:
        """Return true when device is switched on."""
        return self._raw["power_on"]

    @property
    def switch_lock(self) -> bool:
        """
        Return True when switch_lock feature is on.

        Switch lock forces the relay to be turned on. While switch lock is enabled,
        you can't turn off the relay (not with the button, app or API)
        """
        return self._raw["switch_lock"]

    @property
    def brightness(self) -> int:
        """
        Return brightness of status-LED.

        Value between 0 and 255, where 255 is max
        """
        return self._raw["brightness"]

    async def update(self) -> bool:
        """Fetch new data for object."""
        response = await self._request("get", "api/v1/state")
        if response is None:
            return False

        self._raw = response
        return True
