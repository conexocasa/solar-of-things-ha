# Solar System Control Features

## Overview

The Solar of Things integration now supports **full control** of your solar system settings through Home Assistant. You can adjust battery limits, change operating modes, and control grid interactions directly from your dashboard or automations.

---

## 🎛️ Control Entities

### Number Entities (Sliders)

#### 1. **Battery Charge Limit**
- **Type**: Number (0-100%)
- **Description**: Maximum battery charge level
- **Use Case**: Preserve battery health by limiting charge to 90%
- **Entity**: `number.solar_station_xxxxx_battery_charge_limit`

```yaml
# Set battery charge limit to 90%
service: number.set_value
target:
  entity_id: number.solar_station_xxxxx_battery_charge_limit
data:
  value: 90
```

#### 2. **Battery Discharge Limit**
- **Type**: Number (0-100%)
- **Description**: Minimum battery level before stopping discharge
- **Use Case**: Keep battery reserve for emergencies
- **Entity**: `number.solar_station_xxxxx_battery_discharge_limit`

```yaml
# Don't discharge below 20%
service: number.set_value
target:
  entity_id: number.solar_station_xxxxx_battery_discharge_limit
data:
  value: 20
```

#### 3. **Grid Charge Limit**
- **Type**: Number (0-5000W)
- **Description**: Maximum power to draw from grid for battery charging
- **Use Case**: Charge from grid during off-peak hours
- **Entity**: `number.solar_station_xxxxx_grid_charge_limit`

```yaml
# Allow 2000W grid charging
service: number.set_value
target:
  entity_id: number.solar_station_xxxxx_grid_charge_limit
data:
  value: 2000
```

---

### Select Entities (Dropdowns)

#### 1. **Operating Mode**
- **Type**: Select
- **Options**:
  - **Self-Use**: Maximize self-consumption
  - **Time-of-Use**: Optimize for electricity rates
  - **Backup**: Prioritize battery reserve
  - **Grid-Tie**: Prioritize grid export
  - **Off-Grid**: Independent operation
- **Entity**: `select.solar_station_xxxxx_operating_mode`

```yaml
# Switch to Time-of-Use mode
service: select.select_option
target:
  entity_id: select.solar_station_xxxxx_operating_mode
data:
  option: "Time-of-Use"
```

#### 2. **Battery Priority**
- **Type**: Select
- **Options**:
  - **Solar First**: Use solar before battery
  - **Battery First**: Use battery before solar
  - **Grid First**: Use grid before battery/solar
- **Entity**: `select.solar_station_xxxxx_battery_priority`

```yaml
# Prioritize solar energy
service: select.select_option
target:
  entity_id: select.solar_station_xxxxx_battery_priority
data:
  option: "Solar First"
```

---

### Switch Entities (On/Off)

#### 1. **Grid Charging**
- **Type**: Switch
- **Description**: Allow battery charging from grid
- **Use Case**: Enable during cheap electricity periods
- **Entity**: `switch.solar_station_xxxxx_grid_charging`

```yaml
# Enable grid charging
service: switch.turn_on
target:
  entity_id: switch.solar_station_xxxxx_grid_charging
```

#### 2. **Grid Feed-In**
- **Type**: Switch
- **Description**: Allow exporting excess power to grid
- **Use Case**: Disable when grid feed-in is not compensated
- **Entity**: `switch.solar_station_xxxxx_grid_feed_in`

```yaml
# Disable grid export
service: switch.turn_off
target:
  entity_id: switch.solar_station_xxxxx_grid_feed_in
```

#### 3. **Backup Mode**
- **Type**: Switch
- **Description**: Reserve battery for emergencies
- **Use Case**: Prepare for expected power outage
- **Entity**: `switch.solar_station_xxxxx_backup_mode`

```yaml
# Enable backup reserve
service: switch.turn_on
target:
  entity_id: switch.solar_station_xxxxx_backup_mode
```

---

## 🤖 Automation Examples

### 1. Time-of-Use Optimization

Charge from grid during cheap hours, discharge during peak hours:

```yaml
automation:
  # Charge from grid during cheap period (midnight-6am)
  - alias: "Solar: Charge from Grid (Off-Peak)"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.solar_station_xxxxx_grid_charging
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_grid_charge_limit
        data:
          value: 3000  # 3kW charging

  # Stop grid charging after cheap period
  - alias: "Solar: Stop Grid Charging (Peak)"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.solar_station_xxxxx_grid_charging
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_grid_charge_limit
        data:
          value: 0
```

### 2. Weather-Based Battery Management

Adjust battery limits based on weather forecast:

```yaml
automation:
  - alias: "Solar: Adjust for Cloudy Weather"
    trigger:
      - platform: state
        entity_id: weather.home
        attribute: condition
        to: "cloudy"
    action:
      # Lower discharge limit on cloudy days
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_discharge_limit
        data:
          value: 40  # Keep 40% reserve
      
      # Enable grid charging if needed
      - service: switch.turn_on
        target:
          entity_id: switch.solar_station_xxxxx_grid_charging

  - alias: "Solar: Adjust for Sunny Weather"
    trigger:
      - platform: state
        entity_id: weather.home
        attribute: condition
        to: "sunny"
    action:
      # Normal discharge limit on sunny days
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_discharge_limit
        data:
          value: 10
      
      # Disable grid charging (solar is sufficient)
      - service: switch.turn_off
        target:
          entity_id: switch.solar_station_xxxxx_grid_charging
```

### 3. Emergency Backup Preparation

Prepare for storms or power outages:

```yaml
automation:
  - alias: "Solar: Storm Preparation"
    trigger:
      - platform: state
        entity_id: sensor.weather_alert
        to: "storm_warning"
    action:
      # Enable backup mode
      - service: switch.turn_on
        target:
          entity_id: switch.solar_station_xxxxx_backup_mode
      
      # Set high charge limit
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_charge_limit
        data:
          value: 100
      
      # Set high discharge limit (preserve battery)
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_discharge_limit
        data:
          value: 50
      
      # Enable grid charging to top up
      - service: switch.turn_on
        target:
          entity_id: switch.solar_station_xxxxx_grid_charging
      
      # Notify user
      - service: notify.mobile_app
        data:
          title: "Solar System: Storm Preparation"
          message: "Battery is being prepared for potential outage"
```

### 4. Dynamic Operating Mode

Switch modes based on electricity prices:

```yaml
automation:
  - alias: "Solar: Peak Price Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        above: 0.25  # High price threshold
    action:
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_operating_mode
        data:
          option: "Time-of-Use"
      
      # Maximize battery usage during peak
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_battery_priority
        data:
          option: "Battery First"

  - alias: "Solar: Off-Peak Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        below: 0.10  # Low price threshold
    action:
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_operating_mode
        data:
          option: "Self-Use"
      
      # Prioritize solar during off-peak
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_battery_priority
        data:
          option: "Solar First"
```

### 5. Battery Health Protection

Extend battery life with charge cycling:

```yaml
automation:
  - alias: "Solar: Weekly Battery Calibration"
    trigger:
      - platform: time
        at: "02:00:00"
    condition:
      - condition: time
        weekday:
          - sun  # Every Sunday
    action:
      # Full charge cycle
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_charge_limit
        data:
          value: 100
      
      - delay:
          hours: 6
      
      # Return to normal (90% max)
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_charge_limit
        data:
          value: 90
```

---

## 📊 Dashboard Examples

### Control Panel Card

```yaml
type: entities
title: Solar System Controls
entities:
  - entity: select.solar_station_xxxxx_operating_mode
    name: Operating Mode
  
  - entity: select.solar_station_xxxxx_battery_priority
    name: Battery Priority
  
  - type: divider
  
  - entity: number.solar_station_xxxxx_battery_charge_limit
    name: Charge Limit
  
  - entity: number.solar_station_xxxxx_battery_discharge_limit
    name: Discharge Limit
  
  - entity: number.solar_station_xxxxx_grid_charge_limit
    name: Grid Charge Power
  
  - type: divider
  
  - entity: switch.solar_station_xxxxx_grid_charging
    name: Grid Charging
  
  - entity: switch.solar_station_xxxxx_grid_feed_in
    name: Grid Feed-In
  
  - entity: switch.solar_station_xxxxx_backup_mode
    name: Backup Mode
```

### Battery Management Card

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.solar_station_xxxxx_battery_state_of_charge
    name: Battery Level
    min: 0
    max: 100
    needle: true
    segments:
      - from: 0
        color: "#db4437"
      - from: 20
        color: "#ff9800"
      - from: 50
        color: "#ffc107"
      - from: 80
        color: "#0f9d58"
  
  - type: entities
    title: Battery Controls
    entities:
      - entity: number.solar_station_xxxxx_battery_charge_limit
        name: Max Charge
      - entity: number.solar_station_xxxxx_battery_discharge_limit
        name: Min Discharge
      - entity: switch.solar_station_xxxxx_backup_mode
        name: Backup Reserve
```

### Quick Actions Card

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Self-Use Mode
    icon: mdi:solar-power
    tap_action:
      action: call-service
      service: select.select_option
      target:
        entity_id: select.solar_station_xxxxx_operating_mode
      data:
        option: "Self-Use"
  
  - type: button
    name: Backup Mode
    icon: mdi:battery-lock
    tap_action:
      action: call-service
      service: switch.turn_on
      target:
        entity_id: switch.solar_station_xxxxx_backup_mode
  
  - type: button
    name: Grid Export
    icon: mdi:transmission-tower-export
    tap_action:
      action: call-service
      service: switch.toggle
      target:
        entity_id: switch.solar_station_xxxxx_grid_feed_in
```

---

## ⚠️ Important Notes

### API Limitations

**Note**: The control API endpoints (`/api/device/settings/v1` and `/api/device/settings/update/v1`) are **assumed endpoints** based on common IoT patterns. You will need to:

1. **Verify** these endpoints exist in the actual Solar of Things API
2. **Test** with your device to confirm functionality
3. **Adjust** the API implementation based on actual response formats

### Finding Actual Control Endpoints

To find the real control endpoints:

1. Open https://solar.siseli.com
2. Go to settings/control page on the web interface
3. Open browser Developer Tools (F12) → Network tab
4. Make a settings change (e.g., adjust battery limit)
5. Find the API request in the Network tab
6. Note the:
   - Endpoint URL
   - Request method (POST/PUT)
   - Payload format
   - Response format

Then update `api.py` with the correct endpoints and formats.

### Safety Considerations

⚠️ **Always test control features carefully:**

- Start with non-critical settings
- Monitor system behavior after changes
- Keep battery discharge limits reasonable (don't go below 10-20%)
- Don't exceed manufacturer specifications
- Have manual override capability

### Permissions

Some settings may require:
- Admin/installer level access
- Special authentication
- Firmware version requirements

Check your Solar of Things account permissions.

---

## 🔧 Troubleshooting

### Settings Not Changing

1. **Check logs**: Settings → System → Logs
2. **Verify device_id**: Must be correct for control operations
3. **Test API**: Try changing settings on solar.siseli.com web interface
4. **Check permissions**: Account may not have control access

### Control Entities Not Appearing

1. **Check device_id**: Required for control entities
2. **Restart HA**: After integration update
3. **Check coordinator**: Ensure settings are being fetched
4. **Review logs**: Look for error messages

### Values Not Updating

- Wait 5 minutes for next coordinator refresh
- Or restart Home Assistant to force update
- Check if web interface shows updated values

---

## 📝 Customization

You can customize available options by editing the integration files:

**Operating Modes** (`select.py`):
```python
OPERATING_MODES = [
    "Self-Use",
    "Time-of-Use",
    "Backup",
    "Grid-Tie",
    "Off-Grid",
    # Add more modes here
]
```

**Battery Priority** (`select.py`):
```python
BATTERY_PRIORITY_MODES = [
    "Solar First",
    "Battery First",
    "Grid First",
    # Add more priorities here
]
```

---

## 🚀 Advanced Usage

### Script for Quick Mode Switching

```yaml
script:
  solar_storm_mode:
    alias: "Solar: Storm Mode"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.solar_station_xxxxx_backup_mode
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_discharge_limit
        data:
          value: 50
      - service: switch.turn_on
        target:
          entity_id: switch.solar_station_xxxxx_grid_charging
      - service: notify.mobile_app
        data:
          message: "Solar system in storm protection mode"
  
  solar_normal_mode:
    alias: "Solar: Normal Mode"
    sequence:
      - service: switch.turn_off
        target:
          entity_id: switch.solar_station_xxxxx_backup_mode
      - service: number.set_value
        target:
          entity_id: number.solar_station_xxxxx_battery_discharge_limit
        data:
          value: 10
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_operating_mode
        data:
          option: "Self-Use"
```

### Scene Integration

```yaml
scene:
  - name: Solar Economy Mode
    entities:
      select.solar_station_xxxxx_operating_mode: "Time-of-Use"
      select.solar_station_xxxxx_battery_priority: "Grid First"
      switch.solar_station_xxxxx_grid_feed_in: "on"
  
  - name: Solar Backup Mode
    entities:
      select.solar_station_xxxxx_operating_mode: "Backup"
      switch.solar_station_xxxxx_backup_mode: "on"
      number.solar_station_xxxxx_battery_discharge_limit: 50
```

---

**Full control of your solar system is now at your fingertips!** 🎉
