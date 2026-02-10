# Solar of Things - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration for monitoring solar energy systems via the [Solar of Things](https://solar.siseli.com) platform (Siseli solar inverters).

## Features

- **Real-time Monitoring**: Track solar generation, battery status, grid import/export, and load consumption
- **Full System Control**: Adjust battery limits, operating modes, and grid settings
- **Multiple Stations Support**: Configure as many stations and devices as you have access to
- **Comprehensive Sensors**: 
  - PV Input Power
  - AC Output Power
  - Battery Discharge/Charge Current
  - Battery Voltage & State of Charge
  - Grid Feed-in Power
  - Grid Import Power
  - Load Power
  - Monthly Statistics (PV generation, consumption, etc.)
- **Control Entities**:
  - Battery Charge/Discharge Limits (0-100%)
  - Grid Charge Power Limit (0-5000W)
  - Operating Mode Selection (Self-Use, Time-of-Use, Backup, etc.)
  - Battery Priority Mode (Solar First, Battery First, Grid First)
  - Grid Charging Enable/Disable
  - Grid Feed-In Enable/Disable
  - Backup Mode Enable/Disable
- **Auto-calculated Metrics**: Battery power, grid import, and solar coverage percentage
- **Energy Dashboard Compatible**: Sensors work with Home Assistant's Energy Dashboard

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the `solar_of_things` folder from this repository
2. Copy it to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Finding Your Credentials

Before configuring the integration, you need to obtain your IOT Token, Station ID, and Device ID:

1. Log into [https://solar.siseli.com](https://solar.siseli.com)
2. Open your browser's developer tools (press F12)
3. Go to the **Network** tab
4. Refresh the page
5. Look at the API requests (filter by "api" or "attribute")
6. Find and copy:
   - **IOT-Token**: Found in the request headers
   - **deviceId**: Found in request payloads (18-digit number)
   - **stationId**: Found in request payloads (18-digit number)

### Adding the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Solar of Things"
4. Enter your credentials:
   - **IOT Token** (required): Your authentication token
   - **Device ID** (required): For real-time sensor data
   - **Station ID** (optional): For monthly summary statistics

### Multiple Stations

To add multiple stations:
1. Add the integration once for each station/device combination
2. Use different Device IDs for each
3. Each integration instance will create a separate device in Home Assistant

## Available Sensors

### Real-time Sensors (updated every 5 minutes)

| Sensor | Unit | Description |
|--------|------|-------------|
| PV Input Power | W | Solar panel DC power generation |
| AC Output Power | W | AC power output to loads |
| Battery Discharge Current | A | Battery discharge current |
| Battery Charging Current | A | Battery charging current |
| Battery Voltage | V | Battery voltage |
| Battery Power | W | Calculated battery power (discharge - charge) × voltage |
| Battery State of Charge | % | Battery charge percentage |
| Grid Feed-in Power | W | Power exported to grid |
| Grid Import Power | W | Power imported from grid (calculated) |
| Load Power | W | Total load consumption |

### Monthly Sensors (if Station ID provided)

| Sensor | Unit | Description |
|--------|------|-------------|
| Monthly PV Generated | kWh | Total solar generation this month |
| Monthly Solar Coverage | % | Percentage of consumption from solar |

## Control Entities

### Number Entities (Adjustable Values)

| Entity | Range | Description |
|--------|-------|-------------|
| Battery Charge Limit | 0-100% | Maximum battery charge level |
| Battery Discharge Limit | 0-100% | Minimum battery level before stopping discharge |
| Grid Charge Limit | 0-5000W | Maximum power to draw from grid for charging |

### Select Entities (Mode Selection)

| Entity | Options | Description |
|--------|---------|-------------|
| Operating Mode | Self-Use, Time-of-Use, Backup, Grid-Tie, Off-Grid | System operating mode |
| Battery Priority | Solar First, Battery First, Grid First | Energy source priority |

### Switch Entities (On/Off Controls)

| Entity | Description |
|--------|-------------|
| Grid Charging | Allow battery charging from grid |
| Grid Feed-In | Allow exporting excess power to grid |
| Backup Mode | Reserve battery for emergencies |

See [CONTROL_FEATURES.md](CONTROL_FEATURES.md) for detailed control documentation and automation examples.

## Usage Examples

### Energy Dashboard

Add the following sensors to your Energy Dashboard:

- **Solar Production**: `sensor.solar_station_xxxxx_pv_input_power`
- **Grid Consumption**: `sensor.solar_station_xxxxx_grid_import_power`
- **Grid Return**: `sensor.solar_station_xxxxx_grid_feed_in_power`
- **Battery Charge**: `sensor.solar_station_xxxxx_battery_charging_current`
- **Battery Discharge**: `sensor.solar_station_xxxxx_battery_discharge_current`

### Automation Example

```yaml
automation:
  - alias: "Notify when battery is low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_station_xxxxx_battery_state_of_charge
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Solar battery is low ({{ states('sensor.solar_station_xxxxx_battery_state_of_charge') }}%)"
```

### Lovelace Card Example

```yaml
type: entities
title: Solar System
entities:
  - entity: sensor.solar_station_xxxxx_pv_input_power
    name: Solar Generation
  - entity: sensor.solar_station_xxxxx_battery_state_of_charge
    name: Battery Level
  - entity: sensor.solar_station_xxxxx_load_power
    name: Current Load
  - entity: sensor.solar_station_xxxxx_grid_import_power
    name: Grid Import
```

## Troubleshooting

### "Cannot Connect" Error

- Verify your IOT Token is correct and hasn't expired
- Check that your Device ID and Station ID are correct (18-digit numbers)
- Ensure you have internet connectivity
- Token may expire - get a fresh one from the Siseli portal

### No Data Showing

- Wait 5-10 minutes for the first data update
- Check the integration logs: Settings → System → Logs
- Verify your device is online and reporting data at solar.siseli.com

### Sensors Unavailable

- Check if the specific sensor is supported by your inverter model
- Some sensors may only be available during certain conditions (e.g., battery sensors when battery is active)

## API Information

This integration uses the Solar of Things API endpoints:

- **Time-Series Data**: `/api/attribute/keys/history/v1`
- **Monthly Summary**: `/api/stateAttributeSummary/category/yearly`

API documentation: [GitHub - solar-of-things-solar-usage](https://github.com/Hyllesen/solar-of-things-solar-usage)

## Support

For issues, questions, or feature requests:
- Open an issue on [GitHub](https://github.com/yourusername/solar-of-things-ha/issues)
- Check the [API documentation](https://github.com/Hyllesen/solar-of-things-solar-usage)
- Visit the Home Assistant community forums

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- API documentation by [Hyllesen](https://github.com/Hyllesen/solar-of-things-solar-usage)
- Siseli Solar Inverter Systems
- Home Assistant Community

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Siseli or Solar of Things.
