"""Switch platform for Solar of Things integration."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    station_id: str = data["station_id"]
    device_coordinators = data["device_coordinators"]

    entities: list[SwitchEntity] = []

    for device_id, coordinator in device_coordinators.items():
        device_name = (coordinator.device_meta or {}).get("name") or device_id
        entities.extend(
            [
                SolarOfThingsGridChargingSwitch(api, coordinator, station_id, device_id, device_name),
                SolarOfThingsGridFeedInSwitch(api, coordinator, station_id, device_id, device_name),
                SolarOfThingsBackupModeSwitch(api, coordinator, station_id, device_id, device_name),
            ]
        )

    async_add_entities(entities)


class _BaseSwitch(CoordinatorEntity, SwitchEntity):
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


class SolarOfThingsGridChargingSwitch(_BaseSwitch):
    def __init__(self, api, coordinator, station_id: str, device_id: str, device_name: str) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Grid Charging"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_grid_charging"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:transmission-tower"

    @property
    def is_on(self):
        return bool(((self.coordinator.data or {}).get("settings") or {}).get("gridChargingEnabled", False))

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self._api.set_grid_charging, self._device_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._api.set_grid_charging, self._device_id, False)
        await self.coordinator.async_request_refresh()


class SolarOfThingsGridFeedInSwitch(_BaseSwitch):
    def __init__(self, api, coordinator, station_id: str, device_id: str, device_name: str) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Grid Feed-In"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_grid_feed_in"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:transmission-tower-export"

    @property
    def is_on(self):
        return bool(((self.coordinator.data or {}).get("settings") or {}).get("gridFeedInEnabled", False))

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self._api.set_grid_feed_in, self._device_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._api.set_grid_feed_in, self._device_id, False)
        await self.coordinator.async_request_refresh()


class SolarOfThingsBackupModeSwitch(_BaseSwitch):
    def __init__(self, api, coordinator, station_id: str, device_id: str, device_name: str) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Backup Mode"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_backup_mode"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:battery-lock"

    @property
    def is_on(self):
        return bool(((self.coordinator.data or {}).get("settings") or {}).get("backupModeEnabled", False))

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self._api.set_backup_mode, self._device_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._api.set_backup_mode, self._device_id, False)
        await self.coordinator.async_request_refresh()
