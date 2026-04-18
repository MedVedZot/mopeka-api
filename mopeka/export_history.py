import time
from datetime import datetime
from mopeka.client import MopekaClient, load_config


TARGET_DEVICE_ID = "000000000000"
DATE_START = "2026-01-01"
DATE_END   = "2026-04-01"

COLUMNS_TO_EXPORT = [
    "timestamp_iso",
    "device_id",
    "tank_type",
    "tank_height",
    "vertical",
    "propaneButaneRatio",
    "temperature_c",
    "temperature_f",
    "battery_voltage",
    "signal_quality",
    "volume_original_unit",
    "level_cm",
    "level_inches",
    "fill_percent",
    "volume_liters",
    "volume_gallons_us"
]

def main():
    try:
        client = MopekaClient(load_config())
        start_ts = datetime.strptime(DATE_START, "%Y-%m-%d").timestamp()
        end_ts = datetime.strptime(DATE_END, "%Y-%m-%d").replace(hour=23, minute=59, second=59).timestamp()
        
        raw_history = client.get_history(TARGET_DEVICE_ID, start_ts, end_ts)
        if not raw_history:
            print("No data to export.")
            return

        filtered_history = []
        for entry in raw_history:
            filtered_history.append({k: entry[k] for k in COLUMNS_TO_EXPORT if k in entry})

        short_id = TARGET_DEVICE_ID.lstrip('0')
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{short_id}_{now_str}.csv"
        
        client.export_history_csv(filtered_history, filename)
        print(f"Exported {len(filtered_history)} records to {filename}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()