"""The Solar of Things integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SolarOfThingsAPI
from .const import DOMAIN, CONF_DEVICE_ID

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SELECT, Platform.SWITCH]

DEVICE_UPDATE_INTERVAL = timedelta(minutes=5)
STATION_UPDATE_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solar of Things from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = SolarOfThingsAPI(
        iot_token=entry.data["iot_token"],
        time_zone=entry.data.get("time_zone") or entry.options.get("time_zone"),
    )

    station_id = entry.data["station_id"]
    configured_device_id = (entry.data.get(CONF_DEVICE_ID) or "").strip()

    # Station coordinator (device list + monthly)
    station_coordinator = SolarOfThingsStationCoordinator(
        hass=hass,
        api=api,
        station_id=station_id,
    )
    await station_coordinator.async_config_entry_first_refresh()

    # Create one coordinator per device
    devices = station_coordinator.data.get("devices", []) if station_coordinator.data else []

    # If the user configured a specific deviceId, only create entities for that device.
    # (We still keep station-level data like monthly summary.)
    if configured_device_id:
        filtered = [d for d in devices if str(d.get("id")) == configured_device_id]
        if filtered:
            devices = filtered
        else:
            # Fallback: allow the integration to work even if the device isn't returned
            # by the station device list (permissions / pagination / API quirks).
            devices = [{"id": configured_device_id, "name": configured_device_id}]
    device_coordinators: dict[str, SolarOfThingsDeviceCoordinator] = {}

    for dev in devices:
        device_id = str(dev.get("id") or "")
        if not device_id:
            continue

        c = SolarOfThingsDeviceCoordinator(
            hass=hass,
            api=api,
            station_id=station_id,
            device=device_id,
            device_meta=dev,
        )
        await c.async_config_entry_first_refresh()
        device_coordinators[device_id] = c

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "station_id": station_id,
        "station_coordinator": station_coordinator,
        "device_coordinators": device_coordinators,
        "devices": devices,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


class SolarOfThingsStationCoordinator(DataUpdateCoordinator):
    """Fetch station-level data (device list + monthly stats)."""

    def __init__(self, hass: HomeAssistant, api: SolarOfThingsAPI, station_id: str) -> None:
        self.api = api
        self.station_id = station_id
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_station_{station_id}",
            update_interval=STATION_UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            devices = await self.hass.async_add_executor_job(self.api.list_devices, self.station_id)
            monthly = await self.hass.async_add_executor_job(self.api.fetch_monthly_summary, self.station_id)
            return {"devices": devices, "monthly": monthly}
        except Exception as err:
            raise UpdateFailed(f"Station update failed: {err}")


class SolarOfThingsDeviceCoordinator(DataUpdateCoordinator):
    """Fetch device-level telemetry + settings."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SolarOfThingsAPI,
        station_id: str,
        device: str,
        device_meta: dict,
    ) -> None:
        self.api = api
        self.station_id = station_id
        self.device_id = device
        self.device_meta = device_meta
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_device_{device}",
            update_interval=DEVICE_UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            time_series = await self.hass.async_add_executor_job(self.api.fetch_latest_data, self.device_id)
            settings = await self.hass.async_add_executor_job(self.api.fetch_settings, self.device_id)
            return {
                "time_series": time_series,
                "settings": settings,
                "device": self.device_id,
                "station_id": self.station_id,
                "device_meta": self.device_meta,
            }
        except Exception as err:
            raise UpdateFailed(f"Device update failed for {self.device_id}: {err}")
