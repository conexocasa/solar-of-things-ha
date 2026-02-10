# Quick Start Guide

Get your Solar of Things integration running in 5 minutes!

## Prerequisites

- ✅ Home Assistant installed (2023.1+)
- ✅ Access to https://solar.siseli.com
- ✅ At least one solar station configured

## Step 1: Get Your Credentials (2 minutes)

1. Open https://solar.siseli.com in your browser
2. Login to your account
3. Press **F12** to open Developer Tools
4. Click the **Network** tab
5. Refresh the page (**Ctrl+R** or **Cmd+R**)
6. Click on any API request
7. Copy these values:
   - **IOT-Token** from Request Headers
   - **deviceId** from Request Payload (18 digits)
   - **stationId** from Request Payload (18 digits)

![Finding Credentials](https://via.placeholder.com/600x300?text=See+INSTALLATION.md+for+detailed+screenshots)

## Step 2: Install Integration (1 minute)

### Option A: HACS (Recommended)
1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `https://github.com/yourusername/solar-of-things-ha`
4. Install "Solar of Things"

### Option B: Manual
1. Download this repository
2. Copy `solar_of_things` folder to `/config/custom_components/`
3. Restart Home Assistant

## Step 3: Configure (2 minutes)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Solar of Things"**
4. Enter your credentials:
   ```
   IOT Token:  [paste your token]
   Device ID:  [your 18-digit device ID]
   Station ID: [your 18-digit station ID] (optional)
   ```
5. Click **Submit**

## Step 4: Verify (30 seconds)

1. Go to **Settings** → **Devices & Services**
2. Find your "Solar Station" device
3. You should see sensors like:
   - ✅ PV Input Power
   - ✅ Battery State of Charge
   - ✅ Grid Import Power
   - ✅ Load Power

## Step 5: Add to Dashboard (Optional)

### Quick Dashboard Card

```yaml
type: entities
title: My Solar System
entities:
  - sensor.solar_station_xxxxx_pv_input_power
  - sensor.solar_station_xxxxx_battery_state_of_charge
  - sensor.solar_station_xxxxx_load_power
```

See [EXAMPLES.md](EXAMPLES.md) for more advanced cards!

## Troubleshooting

### "Cannot Connect" Error
- ❌ Token expired → Get fresh token from solar.siseli.com
- ❌ Wrong Device/Station ID → Verify 18-digit numbers
- ❌ Network issue → Check firewall/internet

### No Sensors Showing
- ⏱️ Wait 5-10 minutes for first update
- 🔍 Check logs: Settings → System → Logs
- 🌐 Verify device online at solar.siseli.com

### Need Help?
- 📖 [Full Documentation](README.md)
- 🛠️ [Installation Guide](INSTALLATION.md)
- 💡 [Examples](EXAMPLES.md)
- 🐛 [Report Issue](https://github.com/yourusername/solar-of-things-ha/issues)

## Next Steps

- [ ] Add to Energy Dashboard
- [ ] Create automations for low battery alerts
- [ ] Set up notifications for high solar production
- [ ] Explore template sensors for custom calculations

See [EXAMPLES.md](EXAMPLES.md) for ideas!

---

**🎉 Congratulations!** You're now monitoring your solar system in Home Assistant!
