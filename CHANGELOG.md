# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2026-03-07

### Fixed
- **Correct production AppID and server** -- the IOT Open Platform AppID has been
  corrected to `rBrTRfAPXz` (production) targeting `https://solar.siseli.com`.
  The previous release used the test-environment AppID (`JO4DAiNeys`) which was
  only accepted by `test.solar.siseli.com`, causing "account error" (code 20007)
  for every real user account.
- **Password is now MD5-hashed before transmission** -- the Siseli portal sends
  `MD5(plaintext_password)` (lowercase hex) in the login payload. Sending plain
  text returned code 7 "password error" even with valid credentials. The login
  method now applies `hashlib.md5(password).hexdigest()` before building the
  JSON body, matching the portal behaviour confirmed by live API testing.

### Changed
- `API_AUTH_BASE_URL` changed from `https://test.solar.siseli.com` to `https://solar.siseli.com`.
- `IOT_APP_ID` changed from `JO4DAiNeys` to `rBrTRfAPXz`.
- `IOT_APP_SECRET_ENC` updated to the production-AppID encrypted secret.

## [2.3.0] - 2026-03-07

### Changed
- **Authentication now uses User ID / Account** instead of email address.
  The `CONF_EMAIL` config key is replaced by `CONF_USER_ID` (`user_id`).
  The login payload now sends `{"account": ..., "password": ...}` matching
  the Siseli portal's account-login flow.

### Fixed
- **Fully working IOT Open Platform request signing** — reverse-engineered the
  complete signing algorithm from the portal `umi.js` bundle:
  - Secret decryption: `AES-128-CBC(base64(enc_secret), key=MD5(appID)[:16], iv=MD5(appID)[16:])`.
  - Signature: `MD5(HMAC-SHA256(base64(sorted_qs_headers), decrypted_secret))`.
  - The algorithm was **live-tested** against `test.solar.siseli.com/apis/login/account`
    and confirmed to return code `20007` (invalid credentials) rather than the
    previous code `44` (sign error) — proving the signing is now accepted by the server.
- **Correct API base URLs**:
  - Auth/login endpoints: `https://test.solar.siseli.com` (as hardcoded in portal JS).
  - Data endpoints: `https://solar.siseli.com` (unchanged).
  - Login path fixed from `/login/account` (404) → `/apis/login/account` (200).

### Added
- `API_AUTH_BASE_URL`, `IOT_APP_ID`, `IOT_APP_SECRET_ENC` constants in `const.py`.
- `_decrypt_app_secret()`, `_compute_iot_sign()`, `_make_signed_headers()` helpers in `api.py`.
- `pycryptodome>=3.9.0` added to `manifest.json` requirements for AES decryption.

### Migration note
Existing entries that used `email` for auth will need to re-authenticate:
Home Assistant will show a re-auth prompt where you enter your **User ID** and password.
## [2.2.0] - 2026-03-06

### Added
- **Email + Password authentication** (recommended) — the integration now logs in with Siseli portal credentials (`email`, `password`) and handles the full token lifecycle automatically. Users no longer need to copy IOT tokens from DevTools.
- **Automatic token refresh** — `SolarOfThingsAPI._ensure_token_valid()` proactively refreshes the access token 5 minutes before expiry using `POST /login/refresh/access/token` (mirroring the portal JS behaviour). Falls back to re-login with stored credentials if the refresh token has also expired.
- **HA re-auth flow** — if all refresh strategies fail, coordinators call `entry.async_start_reauth()` so HA displays a notification and the user is guided through re-authentication without losing their config.
- **`on_token_refreshed` callback** — fresh tokens are persisted back to the config entry after every refresh, so the integration survives HA restarts without a new login.
- **Legacy IOT-token mode preserved** — users who prefer not to store credentials can still paste a token manually; re-auth is triggered when it expires.
- New `const.py` keys: `CONF_EMAIL`, `CONF_PASSWORD`, `CONF_REFRESH_TOKEN`, `CONF_ACCESS_TOKEN_EXPIRES`, `CONF_REFRESH_TOKEN_EXPIRES`, `API_LOGIN`, `API_REFRESH_TOKEN`, `TOKEN_REFRESH_LEAD_SECONDS`.
- New config-flow steps: `password`, `token`, `reauth_confirm` (step `user` now offers a mode selector).
- `TokenExpiredError` and `AuthenticationError` custom exceptions in `api.py`.

### Changed
- `SolarOfThingsAPI.__init__` signature updated: keyword-only arguments (`email`, `password`, `iot_token`, `refresh_token`, etc.).
- `__init__.py` coordinators now catch `TokenExpiredError` and trigger re-auth instead of silently failing.
- `strings.json` / `translations/en.json` updated for new flow steps and error messages.
- `manifest.json` version bumped to **2.2.0** (`config_flow` version bumped to **3**).

### Known issues
- The `loginType` field value and exact shape of the `/login/account` response are inferred from portal JS analysis; tested against live API but may need adjustment for non-email login types.


## [2.2.0] - 2026-03-06

### Added
- **Email + Password authentication** (recommended) — logs in automatically; no manual token copying needed.
- **Automatic token refresh** — proactively refreshes access token 5 min before expiry via `POST /login/refresh/access/token`; falls back to re-login with stored credentials.
- **HA re-auth flow** — on total token failure, coordinators call `entry.async_start_reauth()` to prompt user without losing config.
- **`on_token_refreshed` callback** — fresh tokens persisted to config entry after every refresh (survives HA restarts).
- **Legacy IOT-token mode preserved** — paste-a-token still works; re-auth triggered on expiry.
- New constants: `CONF_EMAIL`, `CONF_PASSWORD`, `CONF_REFRESH_TOKEN`, `CONF_ACCESS_TOKEN_EXPIRES`, `CONF_REFRESH_TOKEN_EXPIRES`, `API_LOGIN`, `API_REFRESH_TOKEN`, `TOKEN_REFRESH_LEAD_SECONDS`.
- New config-flow steps: `password`, `token`, `reauth_confirm`; step `user` is now a mode selector.
- `TokenExpiredError` and `AuthenticationError` custom exceptions in `api.py`.

### Changed
- `SolarOfThingsAPI.__init__` uses keyword-only arguments.
- Coordinators catch `TokenExpiredError` and trigger re-auth.
- `strings.json`/`translations/en.json` updated for new flow steps.
- `manifest.json` version **2.2.0**, config flow `VERSION = 3`.

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
