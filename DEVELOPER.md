# Developer Documentation

## Project Structure

```
solar_of_things/
├── __init__.py              # Integration setup and coordinator
├── api.py                   # API client for Solar of Things
├── config_flow.py           # Configuration UI flow
├── const.py                 # Constants and sensor definitions
├── manifest.json            # Integration metadata
├── sensor.py                # Sensor entity definitions
├── strings.json             # UI strings
├── translations/            # Localization files
│   └── en.json
├── tests/                   # Unit tests
│   ├── conftest.py
│   └── test_config_flow.py
├── README.md               # User documentation
├── INSTALLATION.md         # Installation guide
├── EXAMPLES.md             # Configuration examples
├── CHANGELOG.md            # Version history
└── LICENSE                 # MIT License
```

## Architecture

### Components

#### 1. API Client (`api.py`)

The `SolarOfThingsAPI` class handles all communication with the Solar of Things API:

- **Authentication**: Uses IOT-Token in request headers
- **Endpoints**:
  - Time-series data: `/api/attribute/keys/history/v1`
  - Monthly summary: `/api/stateAttributeSummary/category/yearly`
- **Methods**:
  - `fetch_latest_data()`: Retrieves the last hour of time-series data
  - `fetch_monthly_summary()`: Gets current month statistics
  - `test_connection()`: Validates credentials

**Key Features**:
- Automatic value extraction from API responses
- Calculation of derived metrics (battery power, grid import)
- Error handling with requests exceptions
- Configurable time ranges

#### 2. Data Coordinator (`__init__.py`)

The `SolarOfThingsDataUpdateCoordinator` manages data updates:

- **Update Interval**: 5 minutes (configurable)
- **Data Fetching**: Async execution via `async_add_executor_job`
- **Error Recovery**: Uses `UpdateFailed` exception for coordinator retry logic
- **Data Structure**:
  ```python
  {
      "time_series": {sensor_key: value, ...},
      "monthly": {monthly_key: value, ...},
      "station_id": "...",
      "device_id": "..."
  }
  ```

#### 3. Sensors (`sensor.py`)

Two sensor classes:

**`SolarOfThingsSensor`** (real-time):
- Reads from `coordinator.data["time_series"]`
- Updates every 5 minutes
- Supports device classes: power, energy, current, voltage, battery
- Availability based on data presence

**`SolarOfThingsMonthlySensor`** (monthly stats):
- Reads from `coordinator.data["monthly"]`
- Only created if station_id is configured
- Energy and percentage sensors

#### 4. Config Flow (`config_flow.py`)

UI-based configuration:

- **User Step**: Collect IOT token, station ID, device ID
- **Validation**: Tests API connection before saving
- **Multi-station**: Supports adding multiple config entries
- **Options Flow**: Allows changing update interval
- **Unique ID**: `{station_id}_{device_id}` to prevent duplicates

## API Reference

### Solar of Things API

#### Time-Series Endpoint

**URL**: `https://solar.siseli.com/api/attribute/keys/history/v1`

**Method**: POST

**Headers**:
```json
{
  "IOT-Token": "your_token_here",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "deviceId": "123456789012345678",
  "startTime": "2024-02-10T00:00:00+08:00",
  "endTime": "2024-02-10T23:59:59+08:00",
  "keys": ["pvInputPower", "acOutputActivePower", ...]
}
```

**Response**:
```json
{
  "data": {
    "pvInputPower": [
      {"ts": 1234567890, "value": 2500},
      {"ts": 1234567900, "value": 2600}
    ],
    "acOutputActivePower": [...]
  }
}
```

#### Monthly Summary Endpoint

**URL**: `https://solar.siseli.com/api/stateAttributeSummary/category/yearly`

**Method**: POST

**Request Body**:
```json
{
  "stationId": "123456789012345678",
  "year": 2024
}
```

**Response**:
```json
{
  "data": {
    "summary": [
      {
        "month": 1,
        "pvGenerated": 201.06,
        "gridImport": 0,
        "gridExport": 0
      }
    ]
  }
}
```

## Data Flow

```
User Configuration
       ↓
Config Entry Created
       ↓
API Client Initialized
       ↓
Coordinator Created
       ↓
Initial Data Fetch
       ↓
Sensors Created
       ↓
┌─────────────────┐
│  Every 5 min    │
│  Coordinator    │
│  Updates Data   │
└────────┬────────┘
         ↓
    Sensors Update
         ↓
    State Changes
         ↓
  HA Event System
```

## Adding New Sensors

### 1. Define Sensor in `const.py`

```python
SENSOR_DEFINITIONS = {
    "newSensorKey": {
        "name": "New Sensor Name",
        "unit": "W",  # or kWh, A, V, %
        "device_class": "power",  # or energy, current, voltage, battery
        "icon": "mdi:icon-name",
    },
}
```

### 2. Add to API Keys

In `api.py`, add the key to the request payload:

```python
payload = {
    "deviceId": self.device_id,
    "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "keys": [
        "pvInputPower",
        "newSensorKey",  # Add here
        # ... other keys
    ],
}
```

### 3. (Optional) Add Calculations

If the sensor value needs calculation, add logic in `fetch_latest_data()`:

```python
if "someValue" in latest_values:
    value = float(latest_values.get("someValue", 0))
    latest_values["newSensorKey"] = value * 2  # Example calculation
```

### 4. Test

Create a test config entry and verify the sensor appears.

## Calculations

### Battery Power

```python
battery_power = (discharge_current - charge_current) × voltage
```

Where:
- Discharge/charge currents are in Amperes (A)
- Voltage is in Volts (V)
- Result is in Watts (W)

### Grid Import Power

```python
grid_import = max(0, ac_output - pv_power + battery_power + feed_in)
```

This is a simplified calculation. In reality:
- Grid import = Load - Solar - Battery discharge + Feed-in
- Negative values indicate grid export (captured by feed_in sensor)

### Solar Coverage Percentage

```python
solar_percentage = (solar_used / total_consumption) × 100
```

Where:
- Solar used = PV generation - Grid export
- Total consumption = Solar used + Grid import

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-homeassistant-custom-component

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_config_flow.py -v

# Run with coverage
pytest --cov=custom_components.solar_of_things --cov-report=html
```

### Manual Testing

1. **Setup Test Instance**:
   ```bash
   # In Home Assistant development container
   hass -c config --debug
   ```

2. **Add Integration**:
   - Go to Settings → Devices & Services
   - Add "Solar of Things"
   - Enter test credentials

3. **Verify Sensors**:
   - Check Developer Tools → States
   - Look for `sensor.solar_station_*` entities
   - Verify values update

4. **Test Updates**:
   - Wait for 5-minute update interval
   - Or trigger manual update in Developer Tools

### Test Cases

- [ ] Config flow with valid credentials
- [ ] Config flow with invalid credentials
- [ ] Multiple station configuration
- [ ] Sensor value updates
- [ ] Sensor availability
- [ ] API connection failure handling
- [ ] Token expiration handling
- [ ] Options flow update interval change

## Contributing

### Development Setup

1. **Fork the repository**

2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/solar-of-things-ha.git
   cd solar-of-things-ha
   ```

3. **Create development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements_dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Code Style

- Follow Home Assistant coding standards
- Use Black for formatting: `black custom_components/solar_of_things/`
- Use isort for imports: `isort custom_components/solar_of_things/`
- Use pylint: `pylint custom_components/solar_of_things/`
- Use mypy for type checking: `mypy custom_components/solar_of_things/`

### Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `pytest`
4. Run linters: `black . && isort . && pylint custom_components/`
5. Commit with meaningful message
6. Push to your fork
7. Create pull request with description

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example: `feat: add support for inverter temperature sensor`

## Debugging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.solar_of_things: debug
```

### Common Issues

#### 1. "Cannot Connect" Error

**Debugging**:
```python
# In api.py, add logging
_LOGGER.debug("API request: %s", payload)
_LOGGER.debug("API response: %s", response.text)
```

**Common causes**:
- Invalid IOT token
- Wrong device/station ID format
- Network connectivity issues
- API endpoint changes

#### 2. Sensors Not Updating

**Check**:
1. Coordinator last update time
2. API response data structure
3. Sensor key mapping
4. Device availability at solar.siseli.com

#### 3. Incorrect Values

**Verify**:
1. Unit conversions
2. Calculation formulas
3. Time synchronization
4. Sample rate (5-minute intervals)

## Performance Considerations

### API Rate Limiting

- Default: 5-minute update interval
- Avoid requests more frequent than 1 minute
- API has 2000 sample limit per request

### Memory Usage

- Coordinator stores latest data only
- No historical data caching
- Lightweight sensor entities

### CPU Usage

- Async operations for API calls
- Minimal processing per update
- Efficient data extraction

## Security

### Token Storage

- Tokens stored in Home Assistant's config entry (encrypted)
- Never log full token values
- Token validation on setup

### API Communication

- HTTPS only
- No credentials in URLs
- Headers for authentication

### Best Practices

- Don't commit tokens to git
- Use `.gitignore` for sensitive files
- Validate all user inputs
- Handle API errors gracefully

## Future Enhancements

### Planned Features

1. **Historical Data Import**
   - Backfill energy statistics
   - Support for custom date ranges

2. **Advanced Calculations**
   - Cost tracking with electricity rates
   - Carbon offset calculations
   - ROI analysis

3. **Additional Sensors**
   - Inverter temperature
   - Daily/weekly/yearly totals
   - Peak power times

4. **Automation Helpers**
   - Services for manual refresh
   - Events for threshold alerts
   - Binary sensors for status

5. **UI Improvements**
   - Custom panel for detailed views
   - Configuration validation
   - Setup wizard

### Contributing Ideas

Have an idea? Open an issue on GitHub to discuss!

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Solar of Things API](https://github.com/Hyllesen/solar-of-things-solar-usage)
- [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
- [HACS Documentation](https://hacs.xyz/docs/publish/start)

## Support

- GitHub Issues: [Report bugs or request features]
- GitHub Discussions: [Ask questions]
- Home Assistant Community: [Get help from users]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
