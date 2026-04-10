# Mopeka Cloud API Client

A small Python client for authenticating against the Mopeka cloud backend and fetching the latest sensor data for devices linked to your account.

This repository is intended for simple direct access to Mopeka sensor data outside the official mobile app. The script authenticates through AWS Cognito, requests the device list, and then fetches the latest `data-shadow` payload for each device.

## Features

- Authenticates with Mopeka cloud credentials
- Fetches the list of devices on the account
- Requests the latest telemetry entry for each sensor
- Prints raw JSON for easy inspection and further parsing
- Minimal dependency footprint

## Repository structure

```text
mopeka/
├── __init__.py
├── client.py
├── config.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.9 or newer
- A Mopeka account
- Network access to the Mopeka cloud endpoint

## Dependencies

The project currently depends on:

- `requests`
- `pycognito`

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

- `username`: your Mopeka account email
- `password`: your Mopeka account password
- `user_pool_id`: AWS Cognito user pool ID used by the service
- `client_id`: AWS Cognito client ID used by the service
- `base_url`: base API endpoint for sensor requests

Important:
- Do not commit real credentials to a public repository
- The sample `config.json` in this repo should contain placeholders only
- Add your real credentials locally before running the script

## Usage

Run the client:

```bash
python client.py
```

The script will:

1. Load `config.json`
2. Authenticate via Cognito
3. Request the device list
4. Fetch the latest telemetry payload for each device
5. Print the latest item as formatted JSON

## Example output

```text
--- Propane Tank Left (AA:BB:CC:DD:EE:FF) ---
{
  "address": "AA:BB:CC:DD:EE:FF",
  "batteryVoltage": 2.91,
  "temperature": 21.3,
  "tankLevel": 73
}
```

Actual fields depend on the response returned by the cloud service.

## How it works

`client.py` performs three core steps:

1. Reads local configuration from `config.json`
2. Uses `pycognito` to authenticate and obtain an access token
3. Sends authenticated GET requests to:
   - the device list endpoint
   - the per-device `data-shadow` endpoint with `limit=1`

The script currently prints the most recent `timeSeries.Items[0]` payload for each device.

## Notes

- This project is intentionally minimal and designed for inspection/testing
- Error handling is basic by design
- The output is raw JSON, which makes it suitable for piping into other tools or adapting for Home Assistant, scripts, or dashboards
- If the cloud API changes, the script may stop working and require updates

## Security

Before publishing publicly:

- verify that `config.json` contains only placeholder values
- rotate credentials immediately if real credentials were ever committed
- consider adding local override files or environment variable support in future revisions

Recommended `.gitignore` addition if you later switch to real local config files:

```gitignore
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
