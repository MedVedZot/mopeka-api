# Mopeka Cloud API Client

**Version:** 1.0.3

<p align="left">
  <a href="https://buymeacoffee.com/MedVedZot">
    <img src="https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&slug=MedVedZot&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff" />
  </a>
</p>
No subscriptions. Just support if you find value.
<br/><br/>

## About

A small Python client for authenticating against the Mopeka cloud backend and fetching the latest sensor data for devices linked to your account.

This repository is intended for simple direct access to Mopeka sensor data outside the official mobile app. The script authenticates through AWS Cognito, requests the device list, and then fetches the latest `data-shadow` payload for each device.

## Purpose and Scope

Most existing Mopeka integrations and scripts are designed to work over Bluetooth and require direct local access to the sensor. This creates a limitation: if a sensor is connected through a Mopeka WiFi bridge (gateway), its data is no longer accessible via Bluetooth and cannot be retrieved directly by typical local integrations.

This project solves that limitation.

Instead of communicating with sensors over Bluetooth, this client works with the Mopeka cloud backend. It authenticates using your account and retrieves sensor data that has already been uploaded by the WiFi gateway.

As a result:

- It allows access to sensors that are only reachable via Mopeka cloud
- It works even when the sensor is remote and not in Bluetooth range
- It enables integration of Mopeka data into custom systems, automation pipelines, and monitoring tools

**Important:**

- This client does NOT read data from Bluetooth devices
- It ONLY retrieves data from the Mopeka cloud API
- Only sensors linked to your account and reporting through a WiFi bridge will be available

Typical use cases:

- Remote monitoring without Bluetooth access
- Data collection for analytics or alerting
- Using Mopeka data without the official mobile app
- Integration into custom automation systems

## Features

- Authenticates with Mopeka cloud credentials via AWS Cognito
- Token caching with automatic refresh on expiration
- Automatic retry on authentication failures (401/403)
- Session reuse with persistent HTTP headers
- Proper exception handling (MopekaError)
- Fetches historical sensor data with pagination support
- Export historical data to CSV format
- Provides temperature in both Celsius and Fahrenheit
- Calculates history depth and start date from TTL
- Fetches the list of devices on the account
- Requests the latest telemetry entry for each sensor
- level measurements in centimeters and inches
- Provides volume data in Liters, US Gallons, Imperial Gallons, and original units
- Automatically parses tank types (e.g., "500L", "100lb", "200gal") to determine capacity and units
- Accurate volume calculation using circular segment formulas for horizontal tanks and linear approximation for vertical ones
- Correctly handles Propane density when converting between weight (lb) and volume (L)
- Normalizes DynamoDB responses into standard JSON data types
- Converts timestamps to human-readable ISO 8601 UTC formats
- Calculates tank percentages based on tank height (two methods)
- Supports configuration via JSON file or environment variable
- Configurable timeout and AWS region
- Prints normalized JSON for easy inspection and further parsing
- Minimal dependency footprint

## Repository structure

```
MOPEKA_API/
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── mopeka/                         # Python package
    ├── __init__.py                 # Package exports
    ├── __version__.py              # Version information
    ├── client.py                   # MopekaClient class
    ├── run.py                      # Console runner
    ├── read_history.py             # Console runner read history date
    ├── export_history.py           # Console runner export history date
    └── config.json                 # Configuration
```

## Requirements

- Python 3.9 or newer
- A Mopeka account
- Network access to the Mopeka cloud endpoint

## Dependencies

The project currently depends on:

- requests
- pycognito

Install them with:

```bash
pip install -r requirements.txt
```

## Configuration

The script loads settings from `config.json` located in the `mopeka/` directory, or from a path specified by the `MOPEKA_CONFIG` environment variable.

Example `mopeka/config.json`:

```json
{
  "username": "email",
  "password": "password",
  "user_pool_id": "us-east-1_sLQ1KlStp",
  "client_id": "7dafulgmkck7u9hiju6v6p1emt",
  "base_url": "https://gateway.mopeka.cloud/app/sensors",
  "timeout": 20,
  "region": "us-east-1"
}
```

Required fields:

- username: your Mopeka account email
- password: your Mopeka account password
- user_pool_id: AWS Cognito user pool ID used by the service
- client_id: AWS Cognito client ID used by the service
- base_url: base API endpoint for sensor requests

Optional fields:

- region: AWS region for Cognito, defaults to "us-east-1"
- timeout: HTTP request timeout in seconds, defaults to 20

**Note:** Tank height and orientation (vertical/horizontal) are automatically retrieved from the server. The client uses these parameters to apply the correct geometric model for volume and fill percentage calculations.

**Important:**

- Do not commit real credentials to a public repository
- The sample config.json in this repo should contain placeholders only
- Add your real credentials locally before running the script

## Usage

### Console runner

Run the client from project root to fetch current sensor data:

```bash
python run.py
```

The script will:

- Load configuration
- Authenticate via Cognito
- Fetch the system configuration
- Request the device list and full state for each device
- Print normalized data as formatted JSON with human-readable update times

### Reading historical data

To read historical sensor data for a specific date range, edit `read_history.py` and configure:

- `TARGET_DEVICE_ID` - The device ID to query (e.g., "00000080E21D")
- `DATE_START` - Start date in "YYYY-MM-DD" format
- `DATE_END` - End date in "YYYY-MM-DD" format
- `COLUMNS_TO_SHOW` - List of fields to display (comment out unwanted fields)

Run the script:

```bash
python read_history.py
```

The script will:
- Authenticate and fetch the device list
- Retrieve historical data for the specified date range
- Handle pagination automatically for large datasets
- Display selected columns in pipe-separated format
- Show total records retrieved

### Exporting historical data to CSV

To export historical data to a CSV file, edit `export_history.py` and configure:

- `TARGET_DEVICE_ID` - The device ID to query
- `DATE_START` - Start date in "YYYY-MM-DD" format
- `DATE_END` - End date in "YYYY-MM-DD" format
- `COLUMNS_TO_EXPORT` - List of fields to include in CSV

Run the script:

```bash
python export_history.py
```

The script will:
- Fetch historical data for the specified date range
- Filter to include only specified columns
- Export to a CSV file named `export_{device_id}_{timestamp}.csv`
- Display the filename and record count

### As a library

```python
from mopeka.client import MopekaClient, load_config

# Loads from mopeka/config.json or MOPEKA_CONFIG env var
config = load_config()
client = MopekaClient(config)

# Get full state of all devices with normalized data
states = client.get_full_state()

for state in states:
    print(f"Device: {state.get('name')}")
    print(f"Battery: {state.get('battery_voltage')} V")
    print(f"Fill: {state.get('fill_percent')}% (Volume-based)")
    print(f"Current Volume: {state.get('volume_liters')} Liters")
    print(f"Temperature: {state.get('temperature_c')} C")
    print(f"Updated: {state.get('timestamp_iso')}")
```

## How it works

client.py performs five core steps:

1. Reads configuration and authenticates via Cognito to obtain an access token.
2. Fetches the device list and individual `data-shadow` telemetry.
3. **Geometric Analysis**: If the tank is horizontal, it uses trigonometric formulas to calculate the liquid volume (since height-to-volume ratio is non-linear in cylinders).
4. **Unit Conversion**: Based on the `tankType` (e.g., "500L"), it calculates the remaining volume in multiple units, taking into account propane's physical properties.
5. **Historical Data Retrieval**: For historical queries, the client uses pagination with `exclusiveStartKey` to fetch large datasets, and calculates `history_depth_days` from the TTL (Time To Live) value to determine how far back historical data is available.

### Example output

**Current sensor state:**

```
--- Main Propane Tank (000000000000) ---
{
  "device_id": "000000000000",
  "wifi_gate_id": "A1B2C3D4E5F6",
  "brand": "tankcheck",
  "model_number": 264,
  "name": "Main Propane Tank",
  "tank_type": "500L",
  "tank_height": 0.54,
  "vertical": false,
  "propaneButaneRatio": 1,
  "timestamp_iso": "2026-04-12T17:54:42Z",
  "history_start_date": "2025-12-15T00:00:00Z",
  "history_depth_days": 120,
  "temperature_c": 33,
  "temperature_f": 91,
  "battery_voltage": 3.34,
  "signal_quality": 100,
  "volume_original_unit": "l",
  "level_cm": 37.5,
  "level_inches": 14.76,
  "fill_percent": 74.12,
  "volume_liters": 370.6,
  "volume_gallons_us": 97.9,
  "updated_human_readable": "Updated 13 minutes ago"
}
```

**Historical data output (pipe-separated format):**

```
--- History from 2026-01-15 to 2026-04-12 ---
timestamp_iso: 2026-04-12T17:54:42Z | temperature_c: 33 | fill_percent: 74.12 | volume_liters: 370.6
timestamp_iso: 2026-04-12T12:30:15Z | temperature_c: 32 | fill_percent: 73.85 | volume_liters: 369.25
timestamp_iso: 2026-04-12T07:15:08Z | temperature_c: 31 | fill_percent: 73.50 | volume_liters: 367.50
timestamp_iso: 2026-04-12T02:00:22Z | temperature_c: 30 | fill_percent: 73.20 | volume_liters: 366.00

Total records: 150
```

## Notes

- This project is designed for simple, direct access to Mopeka sensor data
- The output is normalized JSON (not raw DynamoDB format), making it easy to parse
- Token caching and retry logic are built-in for reliability
- If the cloud API changes, the client may stop working and require updates
- The client is packaged as a reusable Python module for integration into other projects

## Security

Before publishing publicly:

- verify that config.json contains only placeholder values
- rotate credentials immediately if real credentials were ever committed
- use environment variables (MOPEKA_CONFIG) in production

Recommended .gitignore addition if you later switch to real local config files:

```
config.local.json
.env
.venv/
__pycache__/
```

## Limitations

- No structured logging (uses Python's built-in exception handling)
- No CLI arguments (configuration via JSON file or environment variable only)
- Synchronous only (no async support)

## Possible future improvements

- Async/await support for better performance with multiple devices
- Built-in polling mode with configurable intervals
- Additional sensor management methods (delete, update sensor)
- Rate limiting and backoff strategies
- Unit tests and integration tests
- Support for more complex tank shapes (spherical, torispherical heads)
- Optional InfluxDB export formats
- CLI arguments for easier configuration and usage
- Structured logging with configurable levels

## Disclaimer

This repository is an independent client for accessing cloud data associated with your own account. Use it only with accounts and devices you are authorized to access. The service provider may change authentication flows or API behavior at any time.

## License

MIT