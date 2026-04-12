import time
import json
from datetime import datetime
from .client import MopekaClient, load_config

TARGET_DEVICE_ID = "000000000000"
DATE_START = "2026-01-01"
DATE_END   = "2026-04-01"

COLUMNS_TO_SHOW = [
    "timestamp_iso",
#    "device_id",
#    "wifi_gate_id",
#    "tank_type",
#    "tank_height_m",
#    "vertical",
#    "propaneButaneRatio",
    "temperature_c",
#    "temperature_f",
#    "battery_voltage",
#    "volume_original_unit",
#    "level_cm",
#    "level_inches",
    "fill_percent",
    "volume_liters"
]

def main():
    try:
        client = MopekaClient(load_config())
        start_ts = datetime.strptime(DATE_START, "%Y-%m-%d").timestamp()
        end_ts = datetime.strptime(DATE_END, "%Y-%m-%d").replace(hour=23, minute=59, second=59).timestamp()
        
        print(f"--- History from {DATE_START} to {DATE_END} ---")
        
        raw_history = client.get_history(TARGET_DEVICE_ID, start_ts, end_ts)
        if not raw_history:
            print("No data found.")
            return

        for entry in raw_history:
            output = " | ".join([f"{k}: {entry[k]}" for k in COLUMNS_TO_SHOW if k in entry])
            print(output)

        print(f"\nTotal records: {len(raw_history)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()