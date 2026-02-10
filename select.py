"""Select platform for Solar of Things integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Operating modes available in the system
OPERATING_MODES = [
    "Self-Use",
    "Time-of-Use",
    "Backup",
    "Grid-Tie",
    "Off-Grid",
]

# Battery priority modes
BATTERY_PRIORITY_MODES = [
    "Solar First",
    "Battery First",
    "Grid First",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar of Things select entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = [
        SolarOfThingsOperatingModeSelect(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
        SolarOfThingsBatteryPrioritySelect(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
    ]
    
    async_add_entities(entities)


class SolarOfThingsOperatingModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for system operating mode."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Operating Mode"
        self._attr_unique_id = f"{entry.entry_id}_operating_mode"
        self._attr_options = OPERATING_MODES
        self._attr_icon = "mdi:cog"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Solar Station {self._entry.data.get('station_id', self._entry.data.get('device_id'))}",
            "manufacturer": "Siseli",
            "model": "Solar Inverter",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("operatingMode")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_operating_mode,
                option
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting operating mode: %s", err)
            raise


class SolarOfThingsBatteryPrioritySelect(CoordinatorEntity, SelectEntity):
    """Select entity for battery priority mode."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Battery Priority"
        self._attr_unique_id = f"{entry.entry_id}_battery_priority"
        self._attr_options = BATTERY_PRIORITY_MODES
        self._attr_icon = "mdi:battery-sync"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Solar Station {self._entry.data.get('station_id', self._entry.data.get('device_id'))}",
            "manufacturer": "Siseli",
            "model": "Solar Inverter",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("batteryPriority")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_battery_priority,
                option
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting battery priority: %s", err)
            raise
