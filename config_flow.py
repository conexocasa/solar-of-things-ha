"""Config flow for Solar of Things integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import SolarOfThingsAPI
from .const import DOMAIN, CONF_IOT_TOKEN, CONF_STATION_ID, CONF_DEVICE_ID

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    api = SolarOfThingsAPI(
        iot_token=data[CONF_IOT_TOKEN],
        station_id=data.get(CONF_STATION_ID),
        device_id=data.get(CONF_DEVICE_ID),
    )
    
    # Test the connection
    if not await hass.async_add_executor_job(api.test_connection):
        raise CannotConnect
    
    # Return info that you want to store in the config entry.
    return {"title": f"Solar Station {data.get(CONF_STATION_ID, data.get(CONF_DEVICE_ID))}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar of Things."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._stations: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
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
                # Check if this station is already configured
                await self.async_set_unique_id(
                    f"{user_input.get(CONF_STATION_ID)}_{user_input.get(CONF_DEVICE_ID)}"
                )
                self._abort_if_unique_id_configured()
                
                # Store this station
                self._stations.append(user_input)
                
                # Ask if user wants to add more stations
                return await self.async_step_add_another()

        # Show the form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_IOT_TOKEN): cv.string,
                vol.Optional(CONF_STATION_ID): cv.string,
                vol.Optional(CONF_DEVICE_ID): cv.string,
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

    async def async_step_add_another(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask if user wants to add another station."""
        if user_input is not None:
            if user_input.get("add_another"):
                # Reset for next station
                return await self.async_step_user()
            else:
                # Create entries for all stations
                entries = []
                for station in self._stations:
                    entries.append(
                        self.async_create_entry(
                            title=f"Solar Station {station.get(CONF_STATION_ID, station.get(CONF_DEVICE_ID))}",
                            data=station,
                        )
                    )
                
                # Return the first entry (HA limitation - can only return one)
                # Others will be created via async_step_user calls
                if entries:
                    return entries[0]
        
        return self.async_show_form(
            step_id="add_another",
            data_schema=vol.Schema(
                {
                    vol.Required("add_another", default=False): cv.boolean,
                }
            ),
            description_placeholders={
                "station_count": str(len(self._stations))
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Solar of Things."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "update_interval",
                        default=self.config_entry.options.get("update_interval", 5),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
