# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-03-05

### Added
- `.github/PULL_REQUEST_TEMPLATE.md` — standardised PR template for HACS default submission.

### Changed
- `hacs.json` updated: added all integration platforms (`sensor`, `number`, `select`, `switch`), enabled `zip_release: true`, and set `filename: solar-of-things-ha.zip` so HACS fetches the correct release asset.
- `manifest.json` version bumped to 2.1.1.

## [2.1.0] - 2026-02-26

### Added
- Auto-discover all device IDs under a station using `POST /apis/device/list` (no need to manually enter deviceId).
- Config flow support for optional `device_id`:
  - Leave blank to create entities for *all* devices found under the station.
  - Provide a `device_id` to restrict HA entities to a single device.

### Changed
- Manifest metadata updated (documentation/issue tracker URLs) and integration version bumped to 2.1.0.

## [2.0.0] - 2024-02-10

### Added
- **Control Features**: Full system control capabilities
  - Number entities for battery charge/discharge limits (0-100%)
  - Number entity for grid charge power limit (0-5000W)
  - Select entity for operating mode (Self-Use, Time-of-Use, Backup, Grid-Tie, Off-Grid)
  - Select entity for battery priority (Solar First, Battery First, Grid First)
  - Switch entity for grid charging enable/disable
  - Switch entity for grid feed-in enable/disable
  - Switch entity for backup mode enable/disable
- Settings API integration for reading and updating device configuration
- Comprehensive control documentation (CONTROL_FEATURES.md)
- Automation examples for time-of-use optimization
- Weather-based battery management examples
- Emergency backup preparation automations
- Dashboard control panel examples

### Changed
- Updated coordinator to fetch device settings
- Enhanced API client with control methods
- Updated README with control features documentation
- Extended translations for new entities

### Technical Details
- New platforms: Number, Select, Switch
- API endpoints: `/api/device/settings/v1`, `/api/device/settings/update/v1`
- Immediate coordinator refresh after control changes
- Proper error handling for control operations

## [1.0.0] - 2024-02-10

### Added
- Initial release of Solar of Things integration
- Real-time sensor monitoring via API
- Support for multiple stations/devices configuration
- Config flow for easy setup via UI
- Comprehensive sensor suite:
  - PV Input Power
  - AC Output Power
  - Battery Discharge/Charge Current
  - Battery Voltage
  - Battery State of Charge
  - Battery Power (calculated)
  - Grid Feed-in Power
  - Grid Import Power (calculated)
  - Load Power
  - Monthly PV Generation (when station ID provided)
- Auto-calculated metrics for battery power and grid usage
- 5-minute update interval with configurable options
- Home Assistant Energy Dashboard compatibility
- Device information for each configured station
- Proper device classes and state classes for all sensors
- Error handling and connection validation
- Support for IOT-Token authentication
- Multi-station support through multiple config entries
- Comprehensive documentation and examples

### Technical Details
- API integration with Solar of Things (Siseli) platform
- Uses time-series and monthly summary API endpoints
- Automatic data fetching via coordinator pattern
- Proper unit conversions (W, A, V, kWh, %)
- Timezone handling (GMT+8)
- Request throttling and error recovery

## [Unreleased]

### Planned Features
- Historical data import for energy statistics
- Configurable calculation methods for derived sensors
- Additional monthly statistics sensors
- Support for multiple devices per station
- Advanced battery cycle tracking
- Cost calculation sensors
- Solar forecast integration
- Customizable sensor polling rates per sensor
- Support for additional inverter models
- Webhook support for real-time updates
- MQTT integration option
- RESTful sensor alternatives
- Diagnostic sensors for API health
- Binary sensors for status alerts

### Known Issues
- Grid import calculation may not exactly match utility bills
- Monthly API doesn't track grid import/export (always returns 0)
- Timezone hardcoded to Asia/Manila (GMT+8)
- Token expiration requires manual renewal
- No retry logic for failed API calls (handled by coordinator)

### Considerations for Future Versions
- Add support for custom timezone configuration
- Implement automatic token refresh mechanism
- Add support for historical data backfill
- Create services for on-demand data refresh
- Add diagnostic mode for troubleshooting
- Support for multiple simultaneous time ranges
- Caching layer for API responses
- Rate limiting protection
- Support for alternative authentication methods

---

## Version History

### How to Upgrade

To upgrade to a new version:

1. **Via HACS**:
   - Go to HACS → Integrations
   - Find "Solar of Things"
   - Click "Update"
   - Restart Home Assistant

2. **Manual**:
   - Download the new version
   - Replace files in `/config/custom_components/solar_of_things/`
   - Restart Home Assistant

### Breaking Changes

None yet (version 1.0.0)

### Migration Guide

None required for version 1.0.0

---

## Release Notes Format

Each release includes:
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

## Support

For questions about changes or upgrade issues:
- Check the [README](README.md)
- Review [INSTALLATION.md](INSTALLATION.md)
- Open an issue on GitHub
