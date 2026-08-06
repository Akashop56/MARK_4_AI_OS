import json
import os
import shutil
import subprocess

class BatteryTool:
    def __init__(self):
        self.name = "battery_tool"
        self.description = (
            "Checks Android battery percentage and charging status by safely reading "
            "/sys/class/power_supply/battery/capacity and "
            "/sys/class/power_supply/battery/status, with fallback to "
            "termux-battery-status command."
        )

    def _read_sysfs_capacity(self, base: str):
        path = os.path.join(base, "capacity")
        try:
            if not os.path.isfile(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            if not raw:
                return None
            value = int(raw)
            if 0 <= value <= 100:
                return value
            return None
        except (ValueError, OSError, UnicodeDecodeError):
            return None

    def _read_sysfs_status(self, base: str):
        path = os.path.join(base, "status")
        try:
            if not os.path.isfile(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            return raw if raw else None
        except (OSError, UnicodeDecodeError):
            return None

    def _get_sysfs_data(self):
        base = "/sys/class/power_supply/battery"
        capacity = self._read_sysfs_capacity(base)
        status = self._read_sysfs_status(base)

        if capacity is None and status is None:
            return None

        data = {}
        if capacity is not None:
            data["percentage"] = capacity
        if status is not None:
            data["status"] = status
            data["is_charging"] = status.upper() in ("CHARGING", "FULL")

        data["source"] = "sysfs" if (capacity is not None and status is not None) else "sysfs_partial"
        return data

    def _get_termux_data(self):
        try:
            if not shutil.which("termux-battery-status"):
                return None

            proc = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode != 0:
                return None

            payload = json.loads(proc.stdout)
            data = {}

            percentage = payload.get("percentage")
            if percentage is not None:
                try:
                    pct = int(percentage)
                    if 0 <= pct <= 100:
                        data["percentage"] = pct
                except (ValueError, TypeError):
                    pass

            raw_status = payload.get("status")
            if raw_status:
                upper_status = raw_status.upper()
                status_map = {
                    "CHARGING": "Charging",
                    "DISCHARGING": "Discharging",
                    "NOT_CHARGING": "Not charging",
                    "FULL": "Full",
                    "UNKNOWN": "Unknown",
                }
                data["status"] = status_map.get(upper_status, raw_status)
                data["is_charging"] = upper_status in ("CHARGING", "FULL")

            if "plugged" in payload:
                data["plugged"] = payload["plugged"]

            if "percentage" not in data and "status" not in data:
                return None

            data["source"] = "termux"
            return data

        except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
            return None
        except Exception:
            return None

    def get_battery_status(self):
        data = self._get_sysfs_data() or {}
        original_source = data.get("source")

        if "percentage" not in data or "status" not in data:
            termux_data = self._get_termux_data()
            if termux_data:
                if data:
                    merged = data.copy()
                    merged.update(termux_data)
                    merged["source"] = "sysfs+termux_fallback"
                    data = merged
                else:
                    data = termux_data

        if "percentage" not in data or "status" not in data:
            return {
                "success": False,
                "data": data if data else None,
                "error": "Battery data incomplete: both percentage and status are required.",
            }

        if "is_charging" not in data:
            data["is_charging"] = data.get("status", "").upper() in ("CHARGING", "FULL")

        return {"success": True, "data": data}

    def execute(self, action: str, **kwargs) -> dict:
        normalized = " ".join(action.lower().split()) if isinstance(action, str) else ""

        if normalized in {"check", "battery", "status", "battery_status", "get_battery_status"}:
            return self.get_battery_status()

        return {
            "success": False,
            "data": None,
            "error": f"Unknown action '{action}'. Supported actions: 'check', 'battery', 'status'.",
        }

if __name__ == "__main__":
    tool = BatteryTool()
    result = tool.execute("check")
    print(json.dumps(result, indent=2, default=str))