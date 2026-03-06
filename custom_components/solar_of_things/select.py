"""Select platform for Solar of Things integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

OPERATING_MODES = ["Self-Use", "Time-of-Use", "Backup", "Grid-Tie", "Off-Grid"]
BATTERY_PRIORITY_MODES = ["Solar First", "Battery First", "Grid First"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    station_id: str = data["station_id"]
    device_coordinators = data["device_coordinators"]

    entities: list[SelectEntity] = []

    for device_id, coordinator in device_coordinators.items():
        device_name = (coordinator.device_meta or {}).get("name") or device_id
        entities.extend(
            [
                SolarOfThingsOperatingModeSelect(api, coordinator, station_id, device_id, device_name),
                SolarOfThingsBatteryPrioritySelect(api, coordinator, station_id, device_id, device_name),
            ]
        )

    async_add_entities(entities)


class _BaseSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, api, coordinator, station_id: str, device_id: str, device_name: str) -> None:
        super().__init__(coordinator)
        self._api = api
        self._station_id = station_id
        self._device_id = device_id
        self._device_name = device_name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._station_id, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Siseli",
            "model": (self.coordinator.data.get("device_meta") or {}).get("model") if self.coordinator.data else None,
            "via_device": (DOMAIN, self._station_id),
        }


class SolarOfThingsOperatingModeSelect(_BaseSelect):
    def __init__(self, api, coordinator, station_id: str, device_id: str, device_name: str) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Operating Mode"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_operating_mode"
        self._attr_options = OPERATING_MODES
        self._attr_icon = "mdi:cog"

    @property
    def current_option(self):
        return ((self.coordinator.data or {}).get("settings") or {}).get("operatingMode")

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(self._api.set_operating_mode, self._device_id, option)
        await self.coordinator.async_request_refresh()


class SolarOfThingsBatteryPrioritySelect(_BaseSelect):
    def __init__(self, api, coordinator, station_id: str, device_id: str, device_name: str) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Battery Priority"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_battery_priority"
        self._attr_options = BATTERY_PRIORITY_MODES
        self._attr_icon = "mdi:battery-sync"

    @property
    def current_option(self):
        return ((self.coordinator.data or {}).get("settings") or {}).get("batteryPriority")

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(self._api.set_battery_priority, self._device_id, option)
        await self.coordinator.async_request_refresh()
