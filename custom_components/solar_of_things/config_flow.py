"""Config flow for Solar of Things integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import SolarOfThingsAPI
from .const import (
    DOMAIN,
    CONF_IOT_TOKEN,
    CONF_STATION_ID,
    CONF_DEVICE_ID,
    CONF_TIME_ZONE,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    api = SolarOfThingsAPI(iot_token=data[CONF_IOT_TOKEN], time_zone=data.get(CONF_TIME_ZONE))

    station_id = data[CONF_STATION_ID]
    device_id = (data.get(CONF_DEVICE_ID) or "").strip()

    try:
        # If the user provides a deviceId, validate it directly.
        # Otherwise validate the station by listing devices and querying the first device.
        if device_id:
            res = await hass.async_add_executor_job(api.fetch_latest_data, device_id)
            ok = bool(res)
        else:
            ok = await hass.async_add_executor_job(api.test_connection, station_id)
    except Exception as err:
        _LOGGER.error("Validation failed: %s", err)
        ok = False
    if not ok:
        raise CannotConnect

    return {"title": f"Solar Station {station_id}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar of Things."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"station_{user_input[CONF_STATION_ID]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IOT_TOKEN): cv.string,
                vol.Required(CONF_STATION_ID): cv.string,
                # Optional: user can force a single device under the station.
                vol.Optional(CONF_DEVICE_ID): cv.string,
                vol.Optional(CONF_TIME_ZONE, default="Asia/Manila"): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/Hyllesen/solar-of-things-solar-usage"
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
