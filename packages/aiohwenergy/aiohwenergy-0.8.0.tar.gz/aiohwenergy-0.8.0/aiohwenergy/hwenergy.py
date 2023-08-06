"""Representation of a HomeWizard Energy device."""
from __future__ import annotations

import logging

import async_timeout
from aiohttp.client import ClientSession

from .data import Data
from .device import Device
from .errors import DisabledError, RequestError, UnsupportedError
from .state import State

_LOGGER = logging.getLogger(__name__)

SUPPORTED_API_VERSION = "v1"
SUPPORTED_DEVICES = ["HWE-P1", "SDM230-wifi", "SDM630-wifi", "HWE-SKT"]


class HomeWizardEnergy:
    """Communicate with a HomeWizard Energy device."""

    _session: ClientSession | None
    _device: Device | None = None
    _data: Data | None = None
    _state: State | None = None

    _close_session: bool = False


    def __init__(self, host: str, clientsession: ClientSession = None):
        """Create a HomeWizard Energy object."""
        _LOGGER.debug("__init__ HomeWizardEnergy")

        self._host = host
        self._session = clientsession

    async def __aenter__(self) -> HomeWizardEnergy:
        return self

    async def __aexit__(self, *_exc_info) -> None:
        """Exit context manager."""
        await self.close()

    @property
    def host(self) -> str:
        """Return the hostname of the device."""
        return self._host

    @property
    def device(self) -> Device | None:
        """Return the device object."""
        return self._device

    @property
    def data(self) -> Data | None:
        """Return the data object."""
        return self._data

    @property
    def state(self) -> State | None:
        """Return the state object."""
        return self._state

    async def initialize(self):
        """Initialize new Device object and validate connection."""

        device: Device = Device(self.request)
        if not await device.update():
            _LOGGER.error("Failed to initalize API")
            return

        # Validate 'device'
        if device.api_version != SUPPORTED_API_VERSION:
            raise UnsupportedError(
                f"Unsupported API version, expected version '{SUPPORTED_API_VERSION}'"
            )

        if device.product_type not in SUPPORTED_DEVICES:
            raise UnsupportedError(f"Unsupported device '{device.product_type}'")

        self._device = device

        # Get /data
        data: Data = Data(self.request)
        status = await data.update()
        if not status:
            _LOGGER.error("Failed to get 'data'")
        else:
            self._data = data

        # For HWE-SKT: Get /state
        if self.device.product_type == "HWE-SKT":
            state: State = State(self.request)
            status = await state.update()
            if not status:
                _LOGGER.error("Failed to get 'state' data")
            else:
                self._state = state


    async def update(self) -> bool:
        """Fetch complete state for available endpoints."""
        _LOGGER.debug("hwenergy update")

        if self.device is not None:
            status = await self.device.update()
            if not status:
                return False

        if self.data is not None:
            status = await self.data.update()
            if not status:
                return False

        if self.state is not None:
            status = await self.state.update()
            if not status:
                return False

        return True

    async def request(self, method: str, path: str, data: object = None) -> object | None:
        """Make a request to the API."""
        if self._session is None:
            self._session = ClientSession()
            self._close_session = True

        url = f"http://{self.host}/{path}"
        headers = {"Content-Type": "application/json"}

        _LOGGER.debug("%s, %s, %s", method, url, data)

        async with async_timeout.timeout(8):
            resp = await self._session.request(
                method,
                url,
                json=data,
                headers=headers,
            )
            _LOGGER.debug("%s, %s", resp.status, await resp.text("utf-8"))

        if resp.status == 403:
            # Known case: API disabled
            raise DisabledError(
                "API disabled. API must be enabled in HomeWizard Energy app"
            )

        if resp.status != 200:
            # Something else went wrong
            raise RequestError(f"API request error ({resp.status})")


        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise RequestError("Unexpected content type")

        return await resp.json()

    async def close(self):
        """Close client session."""
        _LOGGER.debug("Closing clientsession")
        if self._session and self._close_session:
            await self._session.close()
