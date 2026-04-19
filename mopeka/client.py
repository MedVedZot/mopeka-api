import json
import math
import os
import re
import time
import csv
from typing import Any, Dict, List, Optional
import requests
from pycognito import Cognito

class MopekaError(Exception): pass

class MopekaClient:
    CONVERSIONS = {'l': 1.0, 'lb': 0.925, 'gal': 3.78541, 'us_gal': 3.78541, 'imp_gal': 4.54609}
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = str(config["base_url"]).rstrip("/")
        self.timeout = int(config["timeout"])
        self.user_pool_id = config["user_pool_id"]
        self.client_id = config["client_id"]
        self.username = config["username"]
        self.password = config["password"]
        self.region = config["region"]
        self._token: Optional[str] = None
        self._token_exp: float = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15",
            "Origin": "app://localhost",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
        })
    
    def authenticate(self, force: bool = False) -> None:
        if not force and self._token and time.time() < self._token_exp: return
        cognito = Cognito(self.user_pool_id, self.client_id, user_pool_region=self.region, username=self.username)
        try: cognito.authenticate(password=self.password)
        except Exception as exc: raise MopekaError(f"Authentication failed: {exc}")
        self._token = getattr(cognito, "access_token", None)
        expires_in = int(getattr(cognito, "expires_in", 3600) or 3600)
        self._token_exp = time.time() + max(60, expires_in - 60)
        self.session.headers.update({"Auth": self._token})
    
    def _request(self, path: str, method: str = "GET", params: Optional[Dict] = None) -> Any:
        self.authenticate()
        res = self.session.request(method=method, url=f"{self.base_url}{path}", params=params, timeout=self.timeout)
        if res.status_code in (401, 403):
            self.authenticate(force=True)
            res = self.session.request(method=method, url=f"{self.base_url}{path}", params=params, timeout=self.timeout)
        return res.json() if "application/json" in res.headers.get("Content-Type", "") else res.text

    def _parse_value(self, item: Any, key: str, default=None):
        if not item or not isinstance(item, dict) or key not in item: return default
        v = item[key]
        if "S" in v: return v["S"]
        if "N" in v:
            try: return float(v["N"]) if "." in v["N"] or "e" in v["N"] else int(v["N"])
            except: return v["N"]
        return default

    def _format_data(self, raw: Dict, device: Dict) -> Dict:
        val_raw = self._parse_value(raw, "Value", 0)
        val = max(0.0, val_raw - 0.017) if val_raw > 0 else 0.0
        ts_ms = self._parse_value(raw, "Timestamp", 0)
        ts = ts_ms / 1000.0
        ttl = self._parse_value(raw, "ttl", 0)

        diff = int(time.time() - ts)
        
        if diff < 60: hum = "Just now"
        elif diff < 3600: hum = f"{diff // 60} min ago"
        elif diff < 86400: hum = f"{diff // 3600} hours ago"
        else: hum = f"{diff // 86400} days ago"

        h = float(device.get("tankHeight", 0))
        t_type = device.get("tankType", "")
        vrt = device.get("vertical", False)
        cap, unit = self._parse_tank_type(t_type)
        fill = self._calculate_fill_percent(val, h, vrt) if h > 0 else 0.0
        vol_l = self._calculate_volume(fill, cap, unit)

        hist_days, hist_start = 0, None
        if ttl > 0 and ts > 0:
            d_sec = ttl - ts
            hist_days = int(d_sec / 86400)
            hist_start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts - d_sec))

        return {
            "device_id": device.get("address"),
            "wifi_gate_id": self._parse_value(raw, "Source", ""),
            "brand": "tankcheck",
            "model_number": device.get("modelNumber"),
            "name": device.get("name"),
            "tank_type": t_type,
            "tank_height": h,
            "vertical": vrt,
            "propaneButaneRatio": device.get("propaneButaneRatio", 1),
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)) if ts else None,
            "history_start_date": hist_start,
            "history_depth_days": hist_days,
            "temperature_c": int(self._parse_value(raw, "Temp", 0)),
            "temperature_f": int(round((self._parse_value(raw, "Temp", 0) * 9/5) + 32)),
            "battery_voltage": round(self._parse_value(raw, "BatteryLevel", 0), 2),
            "signal_quality": int(self._parse_value(raw, "Quality", 0)),
            "volume_original_unit": unit,
            "level_cm": round(val * 100.0, 1) if val else 0.0,
            "level_inches": round(val * 39.3701, 2) if val else 0.0,
            "fill_percent": fill,
            "volume_liters": vol_l,
            "volume_gallons_us": round(vol_l / 3.78541, 2) if vol_l else 0.0,
            "updated_human_readable": hum
        }

    def _calculate_fill_percent(self, level: float, height: float, vertical: bool) -> float:
        if height <= 0: return 0.0
        x = max(0.0, min(1.0, level / height))
        if vertical or x <= 0 or x >= 1: return round(x * 100.0, 2)
        r, h, k = height / 2.0, level, 4.5
        v_cyl = (math.acos(1 - 2*x) - (1 - 2*x) * math.sin(math.acos(1 - 2*x))) * (r**2) * k * r
        v_heads = (math.pi * (h**2) * (3*r - h)) / 3.0
        v_max = (math.pi * (r**2) * k * r) + (4.0 / 3.0 * math.pi * (r**3))
        return round((v_cyl + v_heads) / v_max * 100.0, 2)

    def _parse_tank_type(self, t_type: str) -> tuple:
        m = re.match(r'^([\d.]+)\s*([a-zA-Z]+)$', str(t_type).strip())
        return (float(m.group(1)), m.group(2).lower()) if m else (None, None)

    def _calculate_volume(self, fill: float, cap: Optional[float], unit: Optional[str]) -> Optional[float]:
        if not cap or not unit: return None
        return round(cap * (fill / 100.0) * self.CONVERSIONS.get(unit, 1.0), 2)

    def get_devices(self) -> List[Dict]:
        d = self._request("", params={"_": int(time.time() * 1000)})
        return d.get("devices", []) if isinstance(d, dict) else []

    def get_history(self, device_id: str, start_ts: float, end_ts: float) -> List[Dict]:
        devs = self.get_devices()
        dev = next((d for d in devs if d.get("address") == device_id), {})
        history, last_key = [], None
        while True:
            p = {"limit": 1000, "shadowLimit": 1, "_": int(time.time() * 1000)}
            if last_key: p["exclusiveStartKey"] = json.dumps(last_key)
            data = self._request(f"/{device_id}/data-shadow", params=p)
            ts_data = data.get("timeSeries", {})
            items = ts_data.get("Items", [])
            if not items: break
            for raw in items:
                ts = self._parse_value(raw, "Timestamp", 0) / 1000.0
                if ts < start_ts: return history
                if ts <= end_ts: history.append(self._format_data(raw, dev))
            last_key = ts_data.get("LastEvaluatedKey") or data.get("LastEvaluatedKey")
            if not last_key: break
        return history

    def get_full_state(self) -> List[Dict]:
        devs = self.get_devices()
        res = []
        for d in devs:
            addr = d.get("address")
            data = self._request(f"/{addr}/data-shadow", params={"limit": 1, "shadowLimit": 1})
            items = data.get("timeSeries", {}).get("Items", [])
            if items: res.append(self._format_data(items[0], d))
        return res

    def export_history_csv(self, history: List[Dict], filename: str):
        if not history: return
        with open(filename, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=history[0].keys())
            w.writeheader()
            w.writerows(history)

def load_config(path: Optional[str] = None) -> Dict:
    p = path or os.environ.get("MOPEKA_CONFIG") or os.path.join(os.path.dirname(__file__), "config.json")
    with open(p, "r", encoding="utf-8") as f: return json.load(f)