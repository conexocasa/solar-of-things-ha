"""Sensor platform for Solar of Things integration."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar of Things sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    
    # Create time-series sensors
    for key, definition in SENSOR_DEFINITIONS.items():
        if not key.startswith("monthly_"):
            entities.append(
                SolarOfThingsSensor(
                    coordinator=coordinator,
                    entry=entry,
                    sensor_key=key,
                    sensor_definition=definition,
                )
            )
    
    # Create monthly sensors if station_id is available
    if entry.data.get("station_id"):
        for key, definition in SENSOR_DEFINITIONS.items():
            if key.startswith("monthly_"):
                entities.append(
                    SolarOfThingsMonthlySensor(
                        coordinator=coordinator,
                        entry=entry,
                        sensor_key=key,
                        sensor_definition=definition,
                    )
                )
    
    async_add_entities(entities)


class SolarOfThingsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solar of Things Sensor."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_definition: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._sensor_key = sensor_key
        self._sensor_definition = sensor_definition
        
        # Entity attributes
        self._attr_name = f"{entry.data.get('station_id', entry.data.get('device_id'))} {sensor_definition['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_native_unit_of_measurement = sensor_definition.get("unit")
        self._attr_icon = sensor_definition.get("icon")
        
        # Set device class based on unit
        unit = sensor_definition.get("unit")
        if unit == "W":
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "kWh":
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif unit == "A":
            self._attr_device_class = SensorDeviceClass.CURRENT
            self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "V":
            self._attr_device_class = SensorDeviceClass.VOLTAGE
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif unit == "%":
            if "battery" in sensor_key.lower():
                self._attr_device_class = SensorDeviceClass.BATTERY
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT

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
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "time_series" in self.coordinator.data:
            value = self.coordinator.data["time_series"].get(self._sensor_key)
            if value is not None:
                try:
                    return round(float(value), 2)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.native_value is not None


class SolarOfThingsMonthlySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solar of Things Monthly Sensor."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_definition: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._sensor_key = sensor_key
        self._sensor_definition = sensor_definition
        
        # Entity attributes
        self._attr_name = f"{entry.data.get('station_id')} {sensor_definition['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_native_unit_of_measurement = sensor_definition.get("unit")
        self._attr_icon = sensor_definition.get("icon")
        
        # Set device class
        unit = sensor_definition.get("unit")
        if unit == "kWh":
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Solar Station {self._entry.data.get('station_id')}",
            "manufacturer": "Siseli",
            "model": "Solar Inverter",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "monthly" in self.coordinator.data:
            value = self.coordinator.data["monthly"].get(self._sensor_key)
            if value is not None:
                try:
                    return round(float(value), 2)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
