import json
import pytest
from pytest import raises

import aiohwenergy
import json
from unittest.mock import AsyncMock, patch


def mock_request_response(
    status: int, data: str, content_type: str = "application/json"
):
    """Return the default mocked config entry data."""

    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.content_type = content_type

    async def return_json():
        return json.loads(data)

    mock_response.json = return_json

    return mock_response


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_initialized_p1_data(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                200,
                '{"product_type": "HWE-P1","product_name": "P1 meter","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
            ),
            mock_request_response(
                200,
                '{"smr_version": 50, "meter_model": "ISKRA 2M550E-1012", "wifi_ssid": "my_wifi", "wifi_strength": 56, "total_power_import_t1_kwh": 123.456, "total_power_import_t2_kwh": 234.567, "total_power_export_t1_kwh": 111.222, "total_power_export_t2_kwh": 222.333, "active_power_w": 600, "active_power_l1_w": 100, "active_power_l2_w": 200, "active_power_l3_w": 300, "total_gas_m3": 40, "gas_timestamp": 211231123456}',
            ),
        ]

        assert api.host == "1.2.3.4"
        assert api.device is None
        assert api.data is None
        assert api.state is None

        await api.initialize()

        assert api.device is not None
        assert api.device.product_type == "HWE-P1"
        assert api.device.product_name == "P1 meter"
        assert api.device.serial == "aabbccddeeff"
        assert api.device.firmware_version == "2.13"
        assert api.device.api_version == "v1"

        assert api.data is not None
        assert api.data.smr_version == 50
        assert api.data.meter_model == "ISKRA 2M550E-1012"
        assert api.data.wifi_ssid == "my_wifi"
        assert api.data.wifi_strength == 56
        assert api.data.total_power_import_t1_kwh == 123.456
        assert api.data.total_power_import_t2_kwh == 234.567
        assert api.data.total_power_export_t1_kwh == 111.222
        assert api.data.total_power_export_t2_kwh == 222.333
        assert api.data.active_power_w == 600
        assert api.data.active_power_l1_w == 100
        assert api.data.active_power_l2_w == 200
        assert api.data.active_power_l3_w == 300
        assert api.data.total_gas_m3 == 40
        assert api.data.gas_timestamp == "2021-12-31T12:34:56"
        assert len(api.data.available_datapoints) == 14

        assert api.state is None


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_initialized_kwh_1_data_data(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                200,
                '{"product_type": "SDM230-wifi","product_name": "kWh meter","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
            ),
            mock_request_response(
                200,
                '{"wifi_ssid": "my_wifi", "wifi_strength": 56, "total_power_import_t1_kwh": 123.456, "total_power_export_t1_kwh": 111.222, "active_power_w": 600, "active_power_l1_w": 100}',
            ),
        ]

        assert api.host == "1.2.3.4"
        assert api.device is None
        assert api.data is None
        assert api.state is None

        await api.initialize()

        assert api.device is not None
        assert api.device.product_type == "SDM230-wifi"
        assert api.device.product_name == "kWh meter"
        assert api.device.serial == "aabbccddeeff"
        assert api.device.firmware_version == "2.13"
        assert api.device.api_version == "v1"

        assert api.data is not None
        assert api.data.meter_model is None
        assert api.data.wifi_ssid == "my_wifi"
        assert api.data.wifi_strength == 56
        assert api.data.total_power_import_t1_kwh == 123.456
        assert api.data.total_power_export_t1_kwh == 111.222
        assert api.data.active_power_w == 600
        assert api.data.active_power_l1_w == 100
        assert len(api.data.available_datapoints) == 6

        assert api.state is None


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_initialized_kwh_3_data_data(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                200,
                '{"product_type": "SDM630-wifi","product_name": "kWh meter","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
            ),
            mock_request_response(
                200,
                '{"wifi_ssid": "my_wifi", "wifi_strength": 56, "total_power_import_t1_kwh": 123.456, "total_power_export_t1_kwh": 111.222, "active_power_w": 600, "active_power_l1_w": 100, "active_power_l2_w": 200, "active_power_l3_w": 300}',
            ),
        ]

        assert api.host == "1.2.3.4"
        assert api.device is None
        assert api.data is None
        assert api.state is None

        await api.initialize()

        assert api.device is not None
        assert api.device.product_type == "SDM630-wifi"
        assert api.device.product_name == "kWh meter"
        assert api.device.serial == "aabbccddeeff"
        assert api.device.firmware_version == "2.13"
        assert api.device.api_version == "v1"

        assert api.data is not None
        assert api.data.meter_model is None
        assert api.data.wifi_ssid == "my_wifi"
        assert api.data.wifi_strength == 56
        assert api.data.total_power_import_t1_kwh == 123.456
        assert api.data.total_power_export_t1_kwh == 111.222
        assert api.data.active_power_w == 600
        assert api.data.active_power_l1_w == 100
        assert api.data.active_power_l2_w == 200
        assert api.data.active_power_l3_w == 300
        assert len(api.data.available_datapoints) == 8

        assert api.state is None


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_initialized_socket_data_data(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                200,
                '{"product_type": "HWE-SKT","product_name": "Energy socket","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
            ),
            mock_request_response(
                200,
                '{"wifi_ssid": "my_wifi", "wifi_strength": 56, "total_power_import_t1_kwh": 123.456, "total_power_export_t1_kwh": 111.222, "active_power_w": 600, "active_power_l1_w": 100}',
            ),
            mock_request_response(
                200, '{"power_on": true, "switch_lock": false, "brightness": 64}'
            ),
        ]

        assert api.host == "1.2.3.4"
        assert api.device is None
        assert api.data is None
        assert api.state is None

        await api.initialize()

        assert api.device is not None
        assert api.device.product_type == "HWE-SKT"
        assert api.device.product_name == "Energy socket"
        assert api.device.serial == "aabbccddeeff"
        assert api.device.firmware_version == "2.13"
        assert api.device.api_version == "v1"

        assert api.data is not None
        assert api.data.meter_model is None
        assert api.data.wifi_ssid == "my_wifi"
        assert api.data.wifi_strength == 56
        assert api.data.total_power_import_t1_kwh == 123.456
        assert api.data.total_power_export_t1_kwh == 111.222
        assert api.data.active_power_w == 600
        assert api.data.active_power_l1_w == 100
        assert len(api.data.available_datapoints) == 6

        assert api.state is not None
        assert api.state.power_on == True
        assert api.state.switch_lock == False
        assert api.state.brightness == 64


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_catches_disabled_api(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                403,
                '{"product_type": "HWE-SKT","product_name": "Energy socket","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
            ),
        ]

        with raises(aiohwenergy.errors.DisabledError):
            await api.initialize()


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_catches_invalid_response(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                404,
                '{"product_type": "HWE-SKT","product_name": "Energy socket","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
            ),
        ]

        with raises(aiohwenergy.errors.RequestError):
            await api.initialize()


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_catches_invalid_content_type(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                200,
                '{"product_type": "HWE-SKT","product_name": "Energy socket","serial": "aabbccddeeff","firmware_version": "2.13","api_version": "v1"}',
                content_type="INVALID",
            ),
        ]

        with raises(aiohwenergy.errors.RequestError):
            await api.initialize()


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_catches_unsupported_api(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(200, '{"api_version": "v_UNSUPPORTED"}'),
        ]

        with raises(aiohwenergy.errors.UnsupportedError):
            await api.initialize()


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_device_catches_unsupported_device(mock):

    async with aiohwenergy.HomeWizardEnergy("1.2.3.4") as api:
        mock.return_value.__aenter__.side_effect = [
            mock_request_response(
                200, '{"product_type": "HWE-INVALID_DEVICE", "api_version": "v1"}'
            ),
        ]

        with raises(aiohwenergy.errors.UnsupportedError):
            await api.initialize()
