"""Switch platform for Solar of Things integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar of Things switch entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = [
        SolarOfThingsGridChargingSwitch(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
        SolarOfThingsGridFeedInSwitch(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
        SolarOfThingsBackupModeSwitch(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
    ]
    
    async_add_entities(entities)


class SolarOfThingsGridChargingSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for grid charging control."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Grid Charging"
        self._attr_unique_id = f"{entry.entry_id}_grid_charging"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:transmission-tower"

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
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("gridChargingEnabled", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_grid_charging,
                True
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning on grid charging: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_grid_charging,
                False
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning off grid charging: %s", err)
            raise


class SolarOfThingsGridFeedInSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for grid feed-in control."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Grid Feed-In"
        self._attr_unique_id = f"{entry.entry_id}_grid_feed_in"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:transmission-tower-export"

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
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("gridFeedInEnabled", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_grid_feed_in,
                True
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning on grid feed-in: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_grid_feed_in,
                False
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning off grid feed-in: %s", err)
            raise


class SolarOfThingsBackupModeSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for backup mode control."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Backup Mode"
        self._attr_unique_id = f"{entry.entry_id}_backup_mode"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:battery-lock"

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
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("backupModeEnabled", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_backup_mode,
                True
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning on backup mode: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_backup_mode,
                False
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning off backup mode: %s", err)
            raise
