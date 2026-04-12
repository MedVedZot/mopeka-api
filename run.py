#!/usr/bin/env python3
import json
import sys
from mopeka.client import MopekaClient, load_config

def main() -> int:
    try:
        cfg = load_config()
        client = MopekaClient(cfg)
        states = client.get_full_state()
        for state in states:
            print(f"--- {state.get('name')} ({state.get('device_id')}) ---")
            print(json.dumps(state, indent=2))
            print()
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())