"""Number platform for Solar of Things integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
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
    """Set up Solar of Things number entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = [
        SolarOfThingsBatteryChargeLimitNumber(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
        SolarOfThingsBatteryDischargeLimitNumber(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
        SolarOfThingsGridChargeLimitNumber(
            coordinator=coordinator,
            entry=entry,
            api=api,
        ),
    ]
    
    async_add_entities(entities)


class SolarOfThingsBatteryChargeLimitNumber(CoordinatorEntity, NumberEntity):
    """Number entity for battery charge limit."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Battery Charge Limit"
        self._attr_unique_id = f"{entry.entry_id}_battery_charge_limit"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_mode = NumberMode.SLIDER
        self._attr_icon = "mdi:battery-arrow-up"

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
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("batteryChargeLimit")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_battery_charge_limit,
                int(value)
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting battery charge limit: %s", err)
            raise


class SolarOfThingsBatteryDischargeLimitNumber(CoordinatorEntity, NumberEntity):
    """Number entity for battery discharge limit."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Battery Discharge Limit"
        self._attr_unique_id = f"{entry.entry_id}_battery_discharge_limit"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_mode = NumberMode.SLIDER
        self._attr_icon = "mdi:battery-arrow-down"

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
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("batteryDischargeLimit")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_battery_discharge_limit,
                int(value)
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting battery discharge limit: %s", err)
            raise


class SolarOfThingsGridChargeLimitNumber(CoordinatorEntity, NumberEntity):
    """Number entity for grid charge limit."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        api,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._api = api
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} Grid Charge Limit"
        self._attr_unique_id = f"{entry.entry_id}_grid_charge_limit"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 5000
        self._attr_native_step = 100
        self._attr_native_unit_of_measurement = "W"
        self._attr_mode = NumberMode.SLIDER
        self._attr_device_class = NumberDeviceClass.POWER
        self._attr_icon = "mdi:transmission-tower-import"

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
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data and "settings" in self.coordinator.data:
            return self.coordinator.data["settings"].get("gridChargeLimit")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_grid_charge_limit,
                int(value)
            )
            # Request immediate coordinator update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting grid charge limit: %s", err)
            raise
