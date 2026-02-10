"""API client for Solar of Things."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import requests

from .const import (
    API_BASE_URL,
    API_TIME_SERIES,
    API_MONTHLY_SUMMARY,
    API_SETTINGS_GET,
    API_SETTINGS_SET,
)

_LOGGER = logging.getLogger(__name__)


class SolarOfThingsAPI:
    """API client for Solar of Things."""

    def __init__(
        self,
        iot_token: str,
        station_id: str | None = None,
        device_id: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self.iot_token = iot_token
        self.station_id = station_id
        self.device_id = device_id
        self.session = requests.Session()
        self.session.headers.update({
            "IOT-Token": self.iot_token,
            "Content-Type": "application/json",
        })

    def fetch_latest_data(self) -> dict[str, Any]:
        """Fetch the latest time-series data."""
        if not self.device_id:
            return {}
        
        # Get data for the last hour
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        payload = {
            "deviceId": self.device_id,
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "keys": [
                "pvInputPower",
                "acOutputActivePower",
                "batteryDischargeCurrent",
                "batteryChargingCurrent",
                "batteryVoltage",
                "feedInPower",
                "batteryPower",
                "batterySOC",
            ],
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_TIME_SERIES}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract latest values from each key
            latest_values = {}
            if "data" in data:
                for key, values in data["data"].items():
                    if values and len(values) > 0:
                        # Get the most recent value
                        latest_values[key] = values[-1]["value"]
            
            # Calculate derived values
            if "batteryVoltage" in latest_values:
                voltage = float(latest_values.get("batteryVoltage", 0))
                discharge = float(latest_values.get("batteryDischargeCurrent", 0))
                charge = float(latest_values.get("batteryChargingCurrent", 0))
                
                # Battery power = (discharge - charge) * voltage
                latest_values["batteryPower"] = (discharge - charge) * voltage
                
                # Grid power can be calculated if we have all components
                pv_power = float(latest_values.get("pvInputPower", 0))
                ac_output = float(latest_values.get("acOutputActivePower", 0))
                feed_in = float(latest_values.get("feedInPower", 0))
                battery_power = latest_values["batteryPower"]
                
                # Grid import = Load - PV - Battery discharge + Feed-in
                # Simplified: Grid = AC output - PV - Battery power + Feed-in
                latest_values["gridPower"] = max(0, ac_output - pv_power + battery_power + feed_in)
                latest_values["loadPower"] = ac_output
            
            return latest_values
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching time-series data: %s", err)
            return {}

    def fetch_monthly_summary(self) -> dict[str, Any]:
        """Fetch monthly summary data."""
        if not self.station_id:
            return {}
        
        # Get current year and month
        now = datetime.now()
        
        payload = {
            "stationId": self.station_id,
            "year": now.year,
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_MONTHLY_SUMMARY}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract current month data
            monthly_data = {}
            if "data" in data and "summary" in data["data"]:
                for month_data in data["data"]["summary"]:
                    if month_data.get("month") == now.month:
                        # PV generation in kWh
                        pv_generated = float(month_data.get("pvGenerated", 0))
                        monthly_data["monthly_pv_generated"] = pv_generated
                        
                        # Note: The API doesn't provide grid import directly
                        # These would need to be calculated from time-series data
                        # For now, we'll just provide PV generation
                        break
            
            return monthly_data
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching monthly summary: %s", err)
            return {}

    def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            # Try to fetch a small amount of data
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=10)
            
            payload = {
                "deviceId": self.device_id,
                "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                "keys": ["pvInputPower"],
            }
            
            response = self.session.post(
                f"{API_BASE_URL}{API_TIME_SERIES}",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException:
            return False

    def fetch_settings(self) -> dict[str, Any]:
        """Fetch current device settings."""
        if not self.device_id:
            return {}
        
        payload = {
            "deviceId": self.device_id,
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_SETTINGS_GET}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract settings from response
            settings = {}
            if "data" in data:
                settings_data = data["data"]
                settings["batteryChargeLimit"] = settings_data.get("batteryChargeLimit", 100)
                settings["batteryDischargeLimit"] = settings_data.get("batteryDischargeLimit", 10)
                settings["gridChargeLimit"] = settings_data.get("gridChargeLimit", 0)
                settings["operatingMode"] = settings_data.get("operatingMode", "Self-Use")
                settings["batteryPriority"] = settings_data.get("batteryPriority", "Solar First")
                settings["gridChargingEnabled"] = settings_data.get("gridChargingEnabled", False)
                settings["gridFeedInEnabled"] = settings_data.get("gridFeedInEnabled", True)
                settings["backupModeEnabled"] = settings_data.get("backupModeEnabled", False)
            
            return settings
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching settings: %s", err)
            return {}

    def set_battery_charge_limit(self, limit: int) -> bool:
        """Set battery charge limit (0-100%)."""
        return self._update_setting("batteryChargeLimit", limit)

    def set_battery_discharge_limit(self, limit: int) -> bool:
        """Set battery discharge limit (0-100%)."""
        return self._update_setting("batteryDischargeLimit", limit)

    def set_grid_charge_limit(self, limit: int) -> bool:
        """Set grid charging power limit (W)."""
        return self._update_setting("gridChargeLimit", limit)

    def set_operating_mode(self, mode: str) -> bool:
        """Set system operating mode."""
        return self._update_setting("operatingMode", mode)

    def set_battery_priority(self, priority: str) -> bool:
        """Set battery priority mode."""
        return self._update_setting("batteryPriority", priority)

    def set_grid_charging(self, enabled: bool) -> bool:
        """Enable or disable grid charging."""
        return self._update_setting("gridChargingEnabled", enabled)

    def set_grid_feed_in(self, enabled: bool) -> bool:
        """Enable or disable grid feed-in."""
        return self._update_setting("gridFeedInEnabled", enabled)

    def set_backup_mode(self, enabled: bool) -> bool:
        """Enable or disable backup mode."""
        return self._update_setting("backupModeEnabled", enabled)

    def _update_setting(self, setting_key: str, value: Any) -> bool:
        """Update a specific setting."""
        if not self.device_id:
            _LOGGER.error("Device ID is required for settings update")
            return False
        
        payload = {
            "deviceId": self.device_id,
            "settings": {
                setting_key: value
            }
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_SETTINGS_SET}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if update was successful
            if "success" in data and data["success"]:
                _LOGGER.info("Successfully updated %s to %s", setting_key, value)
                return True
            else:
                _LOGGER.error("Failed to update %s: %s", setting_key, data.get("message", "Unknown error"))
                return False
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error updating setting %s: %s", setting_key, err)
            return False
