# Example Configurations

## Basic Lovelace Cards

### Simple Status Card

```yaml
type: entities
title: Solar System Status
entities:
  - entity: sensor.solar_station_xxxxx_pv_input_power
    name: Solar Generation
    icon: mdi:solar-power
  - entity: sensor.solar_station_xxxxx_battery_state_of_charge
    name: Battery
    icon: mdi:battery
  - entity: sensor.solar_station_xxxxx_load_power
    name: Load
    icon: mdi:home-lightning-bolt
  - entity: sensor.solar_station_xxxxx_grid_import_power
    name: Grid Import
    icon: mdi:transmission-tower-import
```

### Gauge Cards

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.solar_station_xxxxx_battery_state_of_charge
    name: Battery Level
    min: 0
    max: 100
    needle: true
    severity:
      green: 60
      yellow: 30
      red: 0
  
  - type: gauge
    entity: sensor.solar_station_xxxxx_pv_input_power
    name: Solar Generation
    min: 0
    max: 5000
    needle: true
    unit: W
```

### Power Flow Card (Custom Card Required)

First install the Power Flow Card from HACS, then:

```yaml
type: custom:power-flow-card
entities:
  solar: sensor.solar_station_xxxxx_pv_input_power
  battery: sensor.solar_station_xxxxx_battery_power
  grid: sensor.solar_station_xxxxx_grid_import_power
  home: sensor.solar_station_xxxxx_load_power
  battery_charge: sensor.solar_station_xxxxx_battery_state_of_charge
```

### History Graph

```yaml
type: history-graph
title: Solar Production (24h)
hours_to_show: 24
entities:
  - entity: sensor.solar_station_xxxxx_pv_input_power
    name: Solar
  - entity: sensor.solar_station_xxxxx_load_power
    name: Load
  - entity: sensor.solar_station_xxxxx_grid_import_power
    name: Grid
```

### Statistics Card

```yaml
type: statistics-graph
title: Monthly Solar Statistics
entities:
  - entity: sensor.solar_station_xxxxx_pv_input_power
stat_types:
  - mean
  - max
  - min
period:
  calendar:
    period: month
```

## Automations

### Low Battery Alert

```yaml
automation:
  - alias: "Solar Battery Low"
    description: "Alert when battery drops below 20%"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_station_xxxxx_battery_state_of_charge
        below: 20
    condition:
      - condition: state
        entity_id: sun.sun
        state: "below_horizon"
    action:
      - service: notify.mobile_app
        data:
          title: "Solar Battery Low"
          message: "Battery is at {{ states('sensor.solar_station_xxxxx_battery_state_of_charge') }}%"
          data:
            priority: high
```

### High Solar Production Notification

```yaml
automation:
  - alias: "Solar Production Peak"
    description: "Notify when solar production exceeds threshold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_station_xxxxx_pv_input_power
        above: 4000
        for:
          minutes: 10
    action:
      - service: notify.mobile_app
        data:
          message: "Excellent solar production: {{ states('sensor.solar_station_xxxxx_pv_input_power') }}W!"
```

### Grid Import Alert

```yaml
automation:
  - alias: "High Grid Usage"
    description: "Alert when importing significant power from grid"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_station_xxxxx_grid_import_power
        above: 2000
        for:
          minutes: 15
    condition:
      - condition: state
        entity_id: sun.sun
        state: "above_horizon"
    action:
      - service: notify.mobile_app
        data:
          message: "High grid usage ({{ states('sensor.solar_station_xxxxx_grid_import_power') }}W) despite daylight. Check system."
```

### Daily Solar Summary

```yaml
automation:
  - alias: "Daily Solar Report"
    description: "Send daily solar production summary"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Today's Solar Report"
          message: |
            PV Generated: {{ states('sensor.solar_station_xxxxx_monthly_pv_generated') }} kWh this month
            Current Battery: {{ states('sensor.solar_station_xxxxx_battery_state_of_charge') }}%
            Peak Production: {{ state_attr('sensor.solar_station_xxxxx_pv_input_power', 'max_value') }}W
```

### Smart Device Control

```yaml
automation:
  - alias: "Run Pool Pump on Solar"
    description: "Run pool pump when excess solar available"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_station_xxxxx_pv_input_power
        above: 3000
    condition:
      - condition: numeric_state
        entity_id: sensor.solar_station_xxxxx_battery_state_of_charge
        above: 80
      - condition: numeric_state
        entity_id: sensor.solar_station_xxxxx_grid_import_power
        below: 100
      - condition: time
        after: "10:00:00"
        before: "16:00:00"
    action:
      - service: switch.turn_on
        entity_id: switch.pool_pump
      - delay:
          hours: 2
      - service: switch.turn_off
        entity_id: switch.pool_pump
```

## Scripts

### Calculate Daily Energy

```yaml
script:
  calculate_daily_solar:
    alias: "Calculate Daily Solar Energy"
    sequence:
      - service: utility_meter.calibrate
        data:
          entity_id: sensor.daily_solar_energy
          value: "{{ states('sensor.solar_station_xxxxx_pv_input_power') | float }}"
```

## Template Sensors

Add to your `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "Solar Self Consumption Rate"
        unique_id: solar_self_consumption_rate
        unit_of_measurement: "%"
        state: >
          {% set pv = states('sensor.solar_station_xxxxx_pv_input_power') | float(0) %}
          {% set grid = states('sensor.solar_station_xxxxx_grid_import_power') | float(0) %}
          {% set load = states('sensor.solar_station_xxxxx_load_power') | float(0) %}
          {% if load > 0 %}
            {{ ((load - grid) / load * 100) | round(1) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:percent

      - name: "Solar Battery Status"
        unique_id: solar_battery_status
        state: >
          {% set soc = states('sensor.solar_station_xxxxx_battery_state_of_charge') | float(0) %}
          {% if soc > 80 %}
            Full
          {% elif soc > 50 %}
            Good
          {% elif soc > 20 %}
            Medium
          {% else %}
            Low
          {% endif %}
        icon: >
          {% set soc = states('sensor.solar_station_xxxxx_battery_state_of_charge') | float(0) %}
          {% if soc > 80 %}
            mdi:battery
          {% elif soc > 50 %}
            mdi:battery-70
          {% elif soc > 20 %}
            mdi:battery-30
          {% else %}
            mdi:battery-10
          {% endif %}

      - name: "Solar Power Balance"
        unique_id: solar_power_balance
        unit_of_measurement: "W"
        state: >
          {% set pv = states('sensor.solar_station_xxxxx_pv_input_power') | float(0) %}
          {% set load = states('sensor.solar_station_xxxxx_load_power') | float(0) %}
          {{ (pv - load) | round(0) }}
        icon: mdi:scale-balance
```

## Energy Dashboard Configuration

### Configure Energy Sources

1. Go to **Settings** → **Dashboards** → **Energy**

2. **Grid Consumption**:
   - Click "Add Consumption"
   - Select: `sensor.solar_station_xxxxx_grid_import_power`
   - Use an integration sensor (Riemann sum) if needed

3. **Return to Grid**:
   - Click "Add Grid Return"
   - Select: `sensor.solar_station_xxxxx_grid_feed_in_power`

4. **Solar Panels**:
   - Click "Add Solar Production"
   - Select: `sensor.solar_station_xxxxx_pv_input_power`

5. **Battery**:
   - Click "Add Battery System"
   - Energy going in: `sensor.solar_station_xxxxx_battery_charging_current`
   - Energy going out: `sensor.solar_station_xxxxx_battery_discharge_current`

### Create Integration Sensors

Add to `configuration.yaml` to track total energy:

```yaml
sensor:
  - platform: integration
    source: sensor.solar_station_xxxxx_pv_input_power
    name: Solar Energy Total
    unit_prefix: k
    round: 2
    
  - platform: integration
    source: sensor.solar_station_xxxxx_grid_import_power
    name: Grid Import Energy Total
    unit_prefix: k
    round: 2
    
  - platform: integration
    source: sensor.solar_station_xxxxx_grid_feed_in_power
    name: Grid Export Energy Total
    unit_prefix: k
    round: 2
```

## Custom Dashboard Example

Complete dashboard for comprehensive solar monitoring:

```yaml
title: Solar System
views:
  - title: Overview
    cards:
      - type: vertical-stack
        cards:
          - type: entities
            title: Current Status
            entities:
              - sensor.solar_station_xxxxx_pv_input_power
              - sensor.solar_station_xxxxx_battery_state_of_charge
              - sensor.solar_station_xxxxx_load_power
              - sensor.solar_station_xxxxx_grid_import_power
          
          - type: history-graph
            title: Power Flow (24h)
            hours_to_show: 24
            entities:
              - sensor.solar_station_xxxxx_pv_input_power
              - sensor.solar_station_xxxxx_load_power
              - sensor.solar_station_xxxxx_grid_import_power
          
          - type: gauge
            entity: sensor.solar_station_xxxxx_battery_state_of_charge
            min: 0
            max: 100
            
  - title: Battery
    cards:
      - type: entities
        title: Battery Details
        entities:
          - sensor.solar_station_xxxxx_battery_voltage
          - sensor.solar_station_xxxxx_battery_charging_current
          - sensor.solar_station_xxxxx_battery_discharge_current
          - sensor.solar_station_xxxxx_battery_power
          
  - title: Statistics
    cards:
      - type: statistics-graph
        title: This Month
        entities:
          - sensor.solar_station_xxxxx_pv_input_power
        stat_types:
          - mean
          - max
        period:
          calendar:
            period: month
```
