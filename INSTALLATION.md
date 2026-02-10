# Installation Guide

## Prerequisites

- Home Assistant (2023.1 or newer recommended)
- Access to your Home Assistant configuration directory
- Solar of Things account with at least one configured station

## Step-by-Step Installation

### Method 1: HACS Installation (Recommended)

1. **Install HACS** (if not already installed)
   - Follow the official HACS installation guide: https://hacs.xyz/docs/setup/download

2. **Add Custom Repository**
   - Open HACS in your Home Assistant interface
   - Click on "Integrations"
   - Click the three dots (⋮) in the top right corner
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/yourusername/solar-of-things-ha`
   - Category: Integration
   - Click "Add"

3. **Install the Integration**
   - Find "Solar of Things" in HACS
   - Click "Download"
   - Restart Home Assistant

4. **Configure the Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Solar of Things"
   - Follow the configuration steps

### Method 2: Manual Installation

1. **Download the Integration**
   ```bash
   # SSH into your Home Assistant instance or use the File Editor add-on
   cd /config/custom_components/
   git clone https://github.com/yourusername/solar-of-things-ha.git solar_of_things
   ```

   Or download and extract the ZIP file:
   - Download the latest release from GitHub
   - Extract the `solar_of_things` folder
   - Copy it to `/config/custom_components/`

2. **Verify Installation**
   Your directory structure should look like:
   ```
   /config/
   └── custom_components/
       └── solar_of_things/
           ├── __init__.py
           ├── api.py
           ├── config_flow.py
           ├── const.py
           ├── manifest.json
           ├── sensor.py
           ├── strings.json
           └── translations/
               └── en.json
   ```

3. **Restart Home Assistant**
   - Go to Settings → System → Restart
   - Or use the command: `ha core restart`

4. **Add the Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Solar of Things"
   - Enter your credentials

## Finding Your Credentials

### IOT Token

1. Open https://solar.siseli.com in your browser
2. Log in to your account
3. Press `F12` to open Developer Tools
4. Click on the **Network** tab
5. Refresh the page (`Ctrl+R` or `Cmd+R`)
6. Look for API requests (you can filter by typing "api" in the filter box)
7. Click on any request and look at the **Request Headers** section
8. Find `IOT-Token` and copy its value

**Example:**
```
IOT-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Device ID and Station ID

While still in the Network tab:

1. Look for requests to endpoints like:
   - `/api/attribute/keys/history/v1`
   - `/api/stateAttributeSummary/category/yearly`

2. Click on a request and look at the **Payload** or **Request** section

3. Find values like:
   ```json
   {
     "deviceId": "123456789012345678",
     "stationId": "987654321098765432"
   }
   ```

**Note:** These are 18-digit numbers. Make sure to copy them exactly!

## Configuration Options

When adding the integration, you'll be prompted for:

### Required:
- **IOT Token**: Your authentication token from the Siseli portal

### Optional:
- **Device ID**: Required for real-time sensor data (highly recommended)
- **Station ID**: Required for monthly summary statistics

### Update Interval:
- Default: 5 minutes
- Can be changed in integration options (Settings → Devices & Services → Solar of Things → Configure)
- Recommended range: 1-60 minutes

## Adding Multiple Stations

If you have multiple solar stations:

1. Add the integration once for the first station
2. Go back to Settings → Devices & Services
3. Click "+ Add Integration" again
4. Search for "Solar of Things"
5. Enter the credentials for your second station
6. Repeat for each additional station

Each station will appear as a separate device in Home Assistant.

## Verifying Installation

After installation and configuration:

1. Go to **Settings** → **Devices & Services**
2. Find "Solar of Things" in the integrations list
3. Click on it to see your configured stations
4. Click on a station to see all available sensors
5. Sensors should start showing data within 5-10 minutes

### Expected Sensors

For each configured station, you should see:

**Real-time sensors** (if Device ID provided):
- PV Input Power
- AC Output Power
- Battery Discharge Current
- Battery Charging Current
- Battery Voltage
- Battery Power
- Battery State of Charge
- Grid Feed-in Power
- Grid Import Power
- Load Power

**Monthly sensors** (if Station ID provided):
- Monthly PV Generated

## Troubleshooting Installation

### Integration Not Showing Up

1. **Check file structure**: Ensure all files are in `/config/custom_components/solar_of_things/`
2. **Check file permissions**: Files should be readable by the Home Assistant user
3. **Check logs**: Go to Settings → System → Logs and search for "solar_of_things"
4. **Clear browser cache**: Sometimes the UI needs a hard refresh (`Ctrl+Shift+R`)

### "Cannot Connect" Error

- Verify your IOT Token hasn't expired (tokens may expire after some time)
- Check your Device ID and Station ID are correct (18-digit numbers)
- Ensure Home Assistant can reach https://solar.siseli.com (check firewall/network)
- Get a fresh IOT Token from the Siseli portal

### Sensors Not Updating

1. Wait at least 5-10 minutes after initial configuration
2. Check if your solar system is online at solar.siseli.com
3. Verify the update interval in integration options
4. Check Home Assistant logs for errors

### Permission Denied Errors

If you see permission errors in logs:
```bash
# SSH into Home Assistant
cd /config/custom_components/
chmod -R 755 solar_of_things/
chown -R homeassistant:homeassistant solar_of_things/
```

## Uninstalling

To remove the integration:

1. Go to Settings → Devices & Services
2. Find "Solar of Things"
3. Click the three dots (⋮) next to the integration
4. Select "Delete"
5. Confirm deletion

To completely remove the files:
```bash
rm -rf /config/custom_components/solar_of_things/
```

Then restart Home Assistant.

## Next Steps

After successful installation:

1. [Configure Energy Dashboard](README.md#energy-dashboard)
2. [Create automations](README.md#automation-example)
3. [Add Lovelace cards](README.md#lovelace-card-example)
4. Set up notifications for low battery or high solar production

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting section](README.md#troubleshooting) in README
2. Review Home Assistant logs for error messages
3. Open an issue on GitHub with:
   - Your Home Assistant version
   - Error messages from logs
   - Steps to reproduce the problem
