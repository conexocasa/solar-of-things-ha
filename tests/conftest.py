"""Test configuration for Solar of Things integration."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.solar_of_things.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "iot_token": "test_token_123",
            "station_id": "123456789012345678",
            "device_id": "876543210987654321",
        },
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_api_response():
    """Return mock API response data."""
    return {
        "data": {
            "pvInputPower": [{"ts": 1234567890, "value": 2500}],
            "acOutputActivePower": [{"ts": 1234567890, "value": 1800}],
            "batteryDischargeCurrent": [{"ts": 1234567890, "value": 0}],
            "batteryChargingCurrent": [{"ts": 1234567890, "value": 10}],
            "batteryVoltage": [{"ts": 1234567890, "value": 48}],
            "feedInPower": [{"ts": 1234567890, "value": 500}],
            "batterySOC": [{"ts": 1234567890, "value": 75}],
        }
    }
