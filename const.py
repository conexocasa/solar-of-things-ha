"""Constants for the Solar of Things integration."""

DOMAIN = "solar_of_things"

# Configuration keys
CONF_IOT_TOKEN = "iot_token"
CONF_STATION_ID = "station_id"
CONF_DEVICE_ID = "device_id"

# API endpoints
API_BASE_URL = "https://solar.siseli.com"
API_TIME_SERIES = "/api/attribute/keys/history/v1"
API_MONTHLY_SUMMARY = "/api/stateAttributeSummary/category/yearly"
API_SETTINGS_GET = "/api/device/settings/v1"
API_SETTINGS_SET = "/api/device/settings/update/v1"

# Sensor keys
SENSOR_KEYS = [
    "pvInputPower",
    "acOutputActivePower",
    "batteryDischargeCurrent",
    "batteryChargingCurrent",
    "batteryVoltage",
    "feedInPower",
    "batteryPower",
    "batterySOC",
    "gridPower",
    "loadPower",
]

# Sensor names and units
SENSOR_DEFINITIONS = {
    "pvInputPower": {
        "name": "PV Input Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:solar-power",
    },
    "acOutputActivePower": {
        "name": "AC Output Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:power-plug",
    },
    "batteryDischargeCurrent": {
        "name": "Battery Discharge Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-down",
    },
    "batteryChargingCurrent": {
        "name": "Battery Charging Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-up",
    },
    "batteryVoltage": {
        "name": "Battery Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery",
    },
    "batteryPower": {
        "name": "Battery Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:battery-charging",
    },
    "batterySOC": {
        "name": "Battery State of Charge",
        "unit": "%",
        "device_class": "battery",
        "icon": "mdi:battery",
    },
    "feedInPower": {
        "name": "Grid Feed-in Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:transmission-tower-export",
    },
    "gridPower": {
        "name": "Grid Import Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:transmission-tower-import",
    },
    "loadPower": {
        "name": "Load Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:home-lightning-bolt",
    },
    # Monthly summary sensors
    "monthly_pv_generated": {
        "name": "Monthly PV Generated",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:solar-power",
    },
    "monthly_grid_import": {
        "name": "Monthly Grid Import",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:transmission-tower-import",
    },
    "monthly_total_consumption": {
        "name": "Monthly Total Consumption",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:home-lightning-bolt",
    },
    "monthly_solar_percentage": {
        "name": "Monthly Solar Coverage",
        "unit": "%",
        "icon": "mdi:percent",
    },
}
