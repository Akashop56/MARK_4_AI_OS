import platform
import socket
import time
import os
import sys

try:
    import psutil
except ImportError:
    psutil = None

class SysInfoTool:
    def __init__(self):
        self.name = "sysinfo_tool"
        self.description = "Tool to display system information (CPU, memory, disk, uptime, etc.)"

    def execute(self, action: str, **kwargs) -> dict:
        """Execute the requested system information action."""
        if psutil is None:
            return {
                "success": False,
                "data": {"error": "psutil is required. Install with: pip install psutil"}
            }

        action = action.lower()
        actions = {
            "all": self._get_all_info,
            "cpu": self._get_cpu_info,
            "memory": self._get_memory_info,
            "disk": self._get_disk_info,
            "uptime": self._get_uptime_info,
            "network": self._get_network_info,
            "os": self._get_os_info,
        }

        if action not in actions:
            return {
                "success": False,
                "data": {
                    "error": f"Unknown action '{action}'. Supported actions: {', '.join(sorted(actions))}"
                },
            }

        try:
            data = actions[action]()
            return {"success": True, "data": data}
        except Exception as exc:
            return {"success": False, "data": {"error": str(exc)}}

    def _get_cpu_info(self) -> dict:
        """Gather CPU information."""
        freq = psutil.cpu_freq()
        times = psutil.cpu_times()
        times_dict = times._asdict() if hasattr(times, "_asdict") else dict(times._asdict())

        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "current_frequency_mhz": freq.current if freq else None,
            "min_frequency_mhz": freq.min if freq else None,
            "max_frequency_mhz": freq.max if freq else None,
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "per_core_usage_percent": psutil.cpu_percent(interval=0.1, percpu=True),
            "times": times_dict,
        }

    def _get_memory_info(self) -> dict:
        """Gather memory information."""
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()

        virtual_dict = virtual._asdict() if hasattr(virtual, "_asdict") else dict(virtual._asdict())
        swap_dict = swap._asdict() if hasattr(swap, "_asdict") else dict(swap._asdict())

        return {
            "virtual_memory": virtual_dict,
            "swap_memory": swap_dict,
        }

    def _get_disk_info(self) -> dict:
        """Gather disk information."""
        partitions = []

        for part in psutil.disk_partitions(all=True):
            partition_info = {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "opts": part.opts,
            }

            try:
                usage = psutil.disk_usage(part.mountpoint)
                usage_dict = usage._asdict() if hasattr(usage, "_asdict") else dict(usage._asdict())
                partition_info["usage"] = usage_dict
            except PermissionError:
                partition_info["usage"] = {"error": "Permission denied accessing this mount point"}
            except Exception as exc:
                partition_info["usage"] = {"error": str(exc)}

            partitions.append(partition_info)

        io_counters = psutil.disk_io_counters()
        io_dict = None
        if io_counters:
            io_dict = io_counters._asdict() if hasattr(io_counters, "_asdict") else dict(io_counters._asdict())

        return {
            "partitions": partitions,
            "io_counters": io_dict,
        }

    def _get_uptime_info(self) -> dict:
        """Gather system uptime information."""
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = int(current_time - boot_time)

        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        return {
            "boot_time": boot_time,
            "current_time": current_time,
            "uptime_seconds": uptime_seconds,
            "uptime": {
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
            },
            "human_readable": f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds",
        }

    def _get_network_info(self) -> dict:
        """Gather network information."""
        io_counters = psutil.net_io_counters()
        io_dict = None
        if io_counters:
            io_dict = io_counters._asdict() if hasattr(io_counters, "_asdict") else dict(io_counters._asdict())

        interfaces = {}
        for iface, addrs in psutil.net_if_addrs().items():
            addr_list = []
            for addr in addrs:
                addr_list.append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": getattr(addr, "broadcast", None),
                })
            interfaces[iface] = addr_list

        return {
            "io_counters": io_dict,
            "interfaces": interfaces,
        }

    def _get_os_info(self) -> dict:
        """Gather operating system information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "os_name": os.name,
            "sys_platform": sys.platform,
            "python_version": sys.version,
        }

    def _get_all_info(self) -> dict:
        """Gather all system information."""
        return {
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "uptime": self._get_uptime_info(),
            "network": self._get_network_info(),
            "os": self._get_os_info(),
        }

if __name__ == "__main__":
    tool = SysInfoTool()
    result = tool.execute("all")

    import json
    print(json.dumps(result, indent=2, default=str))