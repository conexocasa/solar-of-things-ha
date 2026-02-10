"""The Solar of Things integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import SolarOfThingsAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SELECT, Platform.SWITCH]

UPDATE_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solar of Things from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create API instance
    api = SolarOfThingsAPI(
        iot_token=entry.data["iot_token"],
        station_id=entry.data.get("station_id"),
        device_id=entry.data.get("device_id")
    )
    
    # Create coordinator
    coordinator = SolarOfThingsDataUpdateCoordinator(
        hass,
        api=api,
        entry=entry,
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class SolarOfThingsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Solar of Things data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SolarOfThingsAPI,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.api = api
        self.entry = entry
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Fetch time-series data
            time_series_data = await self.hass.async_add_executor_job(
                self.api.fetch_latest_data
            )
            
            # Fetch monthly summary if station_id is available
            monthly_data = None
            if self.entry.data.get("station_id"):
                monthly_data = await self.hass.async_add_executor_job(
                    self.api.fetch_monthly_summary
                )
            
            # Fetch device settings
            settings_data = await self.hass.async_add_executor_job(
                self.api.fetch_settings
            )
            
            return {
                "time_series": time_series_data,
                "monthly": monthly_data,
                "settings": settings_data,
                "station_id": self.entry.data.get("station_id"),
                "device_id": self.entry.data.get("device_id"),
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
