# Mopeka Cloud API Client

<p align="left">
  <a href="https://buymeacoffee.com/MedVedZot">
    <img src="https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&slug=MedVedZot&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff" />
  </a>
</p>
<sub>No subscriptions. Just support if you find value.</sub>



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

- Integration into Home Assistant or other automation systems
- Remote monitoring without Bluetooth access
- Data collection for analytics or alerting
- Using Mopeka data without the official mobile app

## Features

- Authenticates with Mopeka cloud credentials
- Fetches the list of devices on the account
- Requests the latest telemetry entry for each sensor
- Prints raw JSON for easy inspection and further parsing
- Minimal dependency footprint

## Repository structure

```
MOPEKA_API/
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── mopeka/
    ├── __init__.py
    ├── client.py
    └── config.json
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

The script loads settings from `config.json` located in the same directory as `client.py`.

Example:

```json
{
  "username": "email",
  "password": "password",
  "user_pool_id": "us-east-1_sLQ1KlStp",
  "client_id": "7dafulgmkck7u9hiju6v6p1emt",
  "base_url": "https://gateway.mopeka.cloud/app/sensors"
}
```

Fields:

- username: your Mopeka account email
- password: your Mopeka account password
- user_pool_id: AWS Cognito user pool ID used by the service
- client_id: AWS Cognito client ID used by the service
- base_url: base API endpoint for sensor requests

**Important:**

- Do not commit real credentials to a public repository
- The sample config.json in this repo should contain placeholders only
- Add your real credentials locally before running the script

## Usage

Run the client:

```bash
python client.py
```

The script will:

- Load config.json
- Authenticate via Cognito
- Request the device list
- Fetch the latest telemetry payload for each device
- Print the latest item as formatted JSON

## Example output

```
--- Propane Tank Main (AA:BB:CC:DD:EE:FF) ---
{
  "Temp": {
    "N": "25"
  },
  "Quality": {
    "N": "75"
  },
  "Source": {
    "S": "12345678-1234-1234-1234-123456789abc"
  },
  "ttl": {
    "N": "1783501377"
  },
  "RawLevel": {
    "N": "10"
  },
  "Button": {
    "N": "0"
  },
  "Value": {
    "N": "0.125"
  },
  "BatteryLevel": {
    "N": "3.12"
  },
  "MAC": {
    "S": "AA:BB:CC:DD:EE:FF"
  },
  "Timestamp": {
    "N": "1775617377956"
  }
}
```

Actual fields depend on the response returned by the cloud service.

## How it works

client.py performs three core steps:

1. Reads local configuration from config.json
2. Uses pycognito to authenticate and obtain an access token
3. Sends authenticated GET requests to:
   - the device list endpoint
   - the per-device data-shadow endpoint with limit=1

The script currently prints the most recent timeSeries.Items[0] payload for each device.

## Notes

- This project is intentionally minimal and designed for inspection/testing
- Error handling is basic by design
- The output is raw JSON, which makes it suitable for piping into other tools or adapting for Home Assistant, scripts, or dashboards
- If the cloud API changes, the script may stop working and require updates

## Security

Before publishing publicly:

- verify that config.json contains only placeholder values
- rotate credentials immediately if real credentials were ever committed
- consider adding local override files or environment variable support in future revisions

Recommended .gitignore addition if you later switch to real local config files:

```
config.local.json
.env
.venv/
__pycache__/
```

## Limitations

- No retries or session reuse
- No structured logging
- No CLI arguments
- No token caching
- No export format besides stdout JSON

## Possible future improvements

- environment variable support
- optional CSV/JSON export
- Home Assistant friendly output
- better exception handling
- polling mode
- packaging as a reusable module

## Disclaimer

This repository is an independent client for accessing cloud data associated with your own account. Use it only with accounts and devices you are authorized to access. The service provider may change authentication flows or API behavior at any time.

## License

MIT
