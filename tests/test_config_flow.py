"""Test the Solar of Things config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.solar_of_things.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    with patch(
        "custom_components.solar_of_things.api.SolarOfThingsAPI.test_connection",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                "iot_token": "test_token",
                "device_id": "123456789012345678",
            },
        )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_form_success(hass: HomeAssistant) -> None:
    """Test successful configuration."""
    with patch(
        "custom_components.solar_of_things.api.SolarOfThingsAPI.test_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                "iot_token": "test_token",
                "device_id": "123456789012345678",
                "station_id": "876543210987654321",
            },
        )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solar Station 876543210987654321"
    assert result["data"] == {
        "iot_token": "test_token",
        "device_id": "123456789012345678",
        "station_id": "876543210987654321",
    }
