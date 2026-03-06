"""API client for Solar of Things (solar.siseli.com)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import requests

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

from .const import (
    API_BASE_URL,
    API_TIME_SERIES,
    API_MONTHLY_SUMMARY,
    API_DEVICE_LIST,
    API_SETTINGS_GET,
    API_SETTINGS_SET,
)

_LOGGER = logging.getLogger(__name__)

_DEFAULT_TZ = "Asia/Manila"


class SolarOfThingsAPI:
    """Solar of Things API wrapper.

    Design note:
    - token + timezone live on this object
    - stationId/deviceId are passed per call (so one integration can handle many devices)
    """

    def __init__(self, iot_token: str, time_zone: str | None = None) -> None:
        self.iot_token = iot_token
        self.time_zone = time_zone or _DEFAULT_TZ

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "IOT-Token": self.iot_token,
                "IOT-Time-Zone": self.time_zone,
                "Origin": "https://solar.siseli.com",
                "Referer": "https://solar.siseli.com/",
                "User-Agent": "HomeAssistant-SolarOfThings/2.1.0 (+https://www.home-assistant.io)",
            }
        )

    def _now(self) -> datetime:
        if ZoneInfo:
            try:
                return datetime.now(tz=ZoneInfo(self.time_zone))
            except Exception:
                return datetime.now()
        return datetime.now()

    def _format_time(self, dt: datetime) -> str:
        """Format timestamp like the Siseli web client expects."""
        if ZoneInfo:
            try:
                dt = dt.astimezone(ZoneInfo(self.time_zone))
            except Exception:
                pass
        return dt.replace(microsecond=0).isoformat()

    # -------------------------
    # Station -> device listing
    # -------------------------
    def list_devices(self, station_id: str, page_size: int = 50) -> list[dict[str, Any]]:
        """Return all devices under a station.

        Uses endpoint discovered from the portal JS bundle: /apis/device/list.
        Expected payload: {page, count, stationId}
        """
        devices: list[dict[str, Any]] = []

        page = 1
        total = None

        while True:
            payload = {"page": page, "count": page_size, "stationId": station_id}
            resp = self.session.post(f"{API_BASE_URL}{API_DEVICE_LIST}", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") not in (0, None):
                raise RuntimeError(f"Device list error code={data.get('code')} message={data.get('message')}")

            d = data.get("data") or {}
            total = d.get("total", total)
            batch = d.get("list") or []
            if not isinstance(batch, list):
                batch = []

            devices.extend(batch)

            if total is None:
                # no pagination info; stop when returned less than requested
                if len(batch) < page_size:
                    break
            else:
                if len(devices) >= int(total):
                    break

            if not batch:
                break

            page += 1

        return devices

    # -------------------------
    # Time-series (per device)
    # -------------------------
    def fetch_latest_data(self, device_id: str) -> dict[str, Any]:
        """Fetch the latest readings for a device."""
        end_time = self._now()
        start_time = end_time - timedelta(hours=1)

        keys = [
            "pvInputPower",
            "acOutputActivePower",
            "batteryDischargeCurrent",
            "batteryChargingCurrent",
            "batteryVoltage",
            "feedInPower",
            "batterySOC",
        ]

        payload = {
            "deviceId": device_id,
            "count": 2000,
            "page": 1,
            "fromTime": self._format_time(start_time),
            "toTime": self._format_time(end_time),
            "orderByTimeAsc": True,
            "keys": keys,
        }

        resp = self.session.post(f"{API_BASE_URL}{API_TIME_SERIES}", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") not in (0, None):
            raise RuntimeError(f"Timeseries error code={data.get('code')} message={data.get('message')}")

        payload_data = (data.get("data") or {}).get("payload") or {}
        fields = payload_data.get("fields") or {}

        latest_values: dict[str, Any] = {}
        for key, arr in fields.items():
            if isinstance(arr, list) and arr:
                latest_values[key] = arr[-1]

        # Unit normalization:
        # - pvInputPower appears to be W
        # - acOutputActivePower is kW in API; normalize to W
        if "acOutputActivePower" in latest_values:
            try:
                latest_values["acOutputActivePower"] = float(latest_values["acOutputActivePower"]) * 1000.0
            except Exception:
                pass

        # Derived values
        voltage = float(latest_values.get("batteryVoltage") or 0)
        discharge = float(latest_values.get("batteryDischargeCurrent") or 0)
        charge = float(latest_values.get("batteryChargingCurrent") or 0)
        latest_values["batteryPower"] = (discharge - charge) * voltage

        pv_power = float(latest_values.get("pvInputPower") or 0)
        ac_output = float(latest_values.get("acOutputActivePower") or 0)
        feed_in = float(latest_values.get("feedInPower") or 0)
        battery_power = float(latest_values.get("batteryPower") or 0)

        latest_values["gridPower"] = max(0.0, ac_output - pv_power + battery_power + feed_in)
        latest_values["loadPower"] = ac_output

        return latest_values

    # -------------------------
    # Monthly summary (station)
    # -------------------------
    def fetch_monthly_summary(self, station_id: str) -> dict[str, Any]:
        """Fetch monthly PV summary for current month."""
        now = self._now()
        year = now.year
        month_key = f"{year}-{str(now.month).zfill(2)}"

        url = (
            f"{API_BASE_URL}{API_MONTHLY_SUMMARY}"
            f"?stationId={station_id}&summaryCategoryKey=pvInverterElectricityQuantityClass"
        )

        resp = self.session.post(url, json={"time": str(year)}, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") not in (0, None):
            raise RuntimeError(f"Monthly summary error code={data.get('code')} message={data.get('message')}")

        props = (((data.get("data") or {}).get("properties")) or [])
        out: dict[str, Any] = {}

        for prop in props:
            prop_key = ((prop.get("property") or {}).get("key"))
            if not prop_key:
                continue
            for tp in prop.get("timePoints") or []:
                if tp.get("time") == month_key and tp.get("isRealValue"):
                    out[prop_key] = tp.get("value")

        if "pvGeneratedEnergy" in out:
            return {"monthly_pv_generated": float(out.get("pvGeneratedEnergy") or 0)}

        return {}

    # -------------------------
    # Settings / control (per device)
    # -------------------------
    def fetch_settings(self, device_id: str) -> dict[str, Any]:
        """Fetch current device settings.

        NOTE: These endpoints may vary by account/device firmware. If your portal uses
        different endpoints, update const.py accordingly.
        """
        payload = {"deviceId": device_id}

        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_SETTINGS_GET}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            settings: dict[str, Any] = {}
            if "data" in data:
                sd = data["data"]
                settings["batteryChargeLimit"] = sd.get("batteryChargeLimit", 100)
                settings["batteryDischargeLimit"] = sd.get("batteryDischargeLimit", 10)
                settings["gridChargeLimit"] = sd.get("gridChargeLimit", 0)
                settings["operatingMode"] = sd.get("operatingMode", "Self-Use")
                settings["batteryPriority"] = sd.get("batteryPriority", "Solar First")
                settings["gridChargingEnabled"] = sd.get("gridChargingEnabled", False)
                settings["gridFeedInEnabled"] = sd.get("gridFeedInEnabled", True)
                settings["backupModeEnabled"] = sd.get("backupModeEnabled", False)

            return settings

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching settings for device %s: %s", device_id, err)
            return {}

    def _update_setting(self, device_id: str, setting_key: str, value: Any) -> bool:
        payload = {"deviceId": device_id, "settings": {setting_key: value}}

        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_SETTINGS_SET}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success") is True or data.get("code") in (0, None):
                _LOGGER.info("Updated %s=%s for device %s", setting_key, value, device_id)
                return True

            _LOGGER.error("Failed to update %s for device %s: %s", setting_key, device_id, data)
            return False

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error updating %s for device %s: %s", setting_key, device_id, err)
            return False

    def set_battery_charge_limit(self, device_id: str, limit: int) -> bool:
        return self._update_setting(device_id, "batteryChargeLimit", limit)

    def set_battery_discharge_limit(self, device_id: str, limit: int) -> bool:
        return self._update_setting(device_id, "batteryDischargeLimit", limit)

    def set_grid_charge_limit(self, device_id: str, limit: int) -> bool:
        return self._update_setting(device_id, "gridChargeLimit", limit)

    def set_operating_mode(self, device_id: str, mode: str) -> bool:
        return self._update_setting(device_id, "operatingMode", mode)

    def set_battery_priority(self, device_id: str, priority: str) -> bool:
        return self._update_setting(device_id, "batteryPriority", priority)

    def set_grid_charging(self, device_id: str, enabled: bool) -> bool:
        return self._update_setting(device_id, "gridChargingEnabled", enabled)

    def set_grid_feed_in(self, device_id: str, enabled: bool) -> bool:
        return self._update_setting(device_id, "gridFeedInEnabled", enabled)

    def set_backup_mode(self, device_id: str, enabled: bool) -> bool:
        return self._update_setting(device_id, "backupModeEnabled", enabled)

    # -------------------------
    # Validation
    # -------------------------
    def test_connection(self, station_id: str) -> bool:
        """Validate token + station by listing devices and calling timeseries on first."""
        try:
            devices = self.list_devices(station_id)
            if not devices:
                return False
            first = devices[0]
            device_id = str(first.get("id") or "")
            if not device_id:
                return False
            _ = self.fetch_latest_data(device_id)
            return True
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
