import json
import time
import requests
import os
from pycognito import Cognito

def load_config():
    base_path = os.path.dirname(__file__)
    path = os.path.join(base_path, 'config.json')
    with open(path, 'r') as f:
        return json.load(f)

def get_auth_token(cfg):
    u = Cognito(
        cfg['user_pool_id'],
        cfg['client_id'],
        user_pool_region="us-east-1",
        username=cfg['username']
    )
    u.authenticate(password=cfg['password'])
    return u.access_token

def fetch_data(url, headers, params=None):
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
        return None
    return resp.json()

def run_mopeka():
    cfg = load_config()
    token = get_auth_token(cfg)
    headers = {"Auth": token, "Accept": "application/json"}
    base_url = cfg['base_url']

    sensors = fetch_data(base_url, headers)
    if not sensors: return

    for dev in sensors.get('devices', []):
        mac, name = dev.get('address'), dev.get('name')
        print(f"--- {name} ({mac}) ---")

        params = {
            "limit": "1",
            "shadowLimit": "1",
            "_": int(time.time() * 1000)
        }

        data = fetch_data(f"{base_url}/{mac}/data-shadow", headers, params)
        if data:
            items = data.get('timeSeries', {}).get('Items', [])
            print(json.dumps(items[0], indent=2) if items else "No data")
        print("\n")

if __name__ == "__main__":
    run_mopeka()