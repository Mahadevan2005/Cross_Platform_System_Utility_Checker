import os
import platform
import uuid
import json
import subprocess
from datetime import datetime
import time
import requests
import psutil

API_ENDPOINT = "http://localhost:8000/api/report"
API_KEY = "secret_key"                      
CACHE_FILE = os.path.expanduser("~/.sysutil_cache.json")
CHECK_INTERVAL_MINUTES = 30                         

# ===== Utility Functions =====

def get_machine_id():
    """Get or create a unique machine ID stored locally."""
    id_file = os.path.expanduser("~/.sysutil_machine_id")
    if os.path.exists(id_file):
        with open(id_file, "r") as f:
            return f.read().strip()
    else:
        machine_id = str(uuid.uuid4())
        with open(id_file, "w") as f:
            f.write(machine_id)
        return machine_id

def check_disk_encryption():
    """Check disk encryption status based on OS."""
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output(["manage-bde", "-status", "C:"], text=True)
            return "Percentage Encrypted: 100%" in output and "Fully Encrypted" in output
        elif system == "Darwin":  # macOS
            output = subprocess.check_output(["fdesetup", "status"], text=True).strip()
            return "FileVault is On" in output
        elif system == "Linux":
            # Check if root is encrypted (basic check for LUKS)
            root_device = subprocess.check_output(["findmnt", "-n", "-o", "SOURCE", "/"]).strip().decode()
            cryptsetup_status = subprocess.run(["cryptsetup", "status", root_device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return cryptsetup_status.returncode == 0
        else:
            return False
    except Exception:
        return False

def check_os_update_status():
    """Check if OS is up to date for Windows, macOS, and Linux."""
    system = platform.system()
    try:
        if system == "Windows":
            # Use PowerShell to check for pending updates
            ps_cmd = [
                "powershell", "-Command",
                "(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search('IsInstalled=0').Updates.Count"
            ]
            output = subprocess.check_output(ps_cmd, text=True).strip()
            pending = int(output)
            current_version = platform.version()
            return {
                "current_version": current_version,
                "latest_version": current_version if pending == 0 else "update available",
                "is_up_to_date": (pending == 0)
            }

        elif system == "Darwin":  # macOS
            output = subprocess.check_output(["softwareupdate", "-l"], text=True)
            pending = "No new software available" not in output
            current_version = subprocess.check_output(
                ["sw_vers", "-productVersion"], text=True
            ).strip()
            return {
                "current_version": current_version,
                "latest_version": current_version if not pending else "update available",
                "is_up_to_date": not pending
            }

        elif system == "Linux":
            # Try apt first
            try:
                output = subprocess.check_output(
                    ["apt", "list", "--upgradable"], stderr=subprocess.DEVNULL, text=True
                )
                pending = len(output.splitlines()) > 1
            except FileNotFoundError:
                # Try dnf
                try:
                    output = subprocess.check_output(
                        ["dnf", "check-update"], stderr=subprocess.DEVNULL, text=True
                    )
                    pending = bool(output.strip())
                except FileNotFoundError:
                    pending = False

            current_version = platform.release()
            return {
                "current_version": current_version,
                "latest_version": current_version if not pending else "update available",
                "is_up_to_date": not pending
            }

        else:
            return {
                "current_version": "unknown",
                "latest_version": "unknown",
                "is_up_to_date": False
            }

    except Exception as e:
        return {
            "current_version": "error",
            "latest_version": "error",
            "is_up_to_date": False,
            "error": str(e)
        }


def check_antivirus():
    """Detect antivirus presence and status."""
    system = platform.system()
    try:
        if system == "Windows":
            # Simple check: Look for common AV processes
            av_processes = ["MsMpEng.exe", "NortonSecurity.exe", "avp.exe", "mcshield.exe"]
            running = [p.name() for p in psutil.process_iter()]
            present = any(av.lower() in (proc.lower() for proc in running) for av in av_processes)
            status = "active" if present else "inactive"
            return {
                "present": present,
                "status": status
            }
        else:
            # On macOS/Linux, this is tricky - we assume no AV installed for demo
            return {
                "present": False,
                "status": "unknown"
            }
    except Exception:
        return {
            "present": False,
            "status": "error"
        }

import re
import subprocess
import platform

import subprocess
import re

def check_inactivity_sleep():
    system = platform.system()

    try:
        if system == "Windows":
            # ===== Windows: use powercfg =====
            scheme_output = subprocess.check_output(
                ["powercfg", "/getactivescheme"], text=True
            )
            scheme_guid = re.search(r"([0-9a-fA-F\-]{36})", scheme_output).group(1)

            query_output = subprocess.check_output(
                ["powercfg", "/query", scheme_guid, "SUB_SLEEP", "STANDBYIDLE"],
                text=True
            )

            ac_match = re.search(r"Current AC Power Setting Index:\s*0x([0-9a-fA-F]+)", query_output)
            dc_match = re.search(r"Current DC Power Setting Index:\s*0x([0-9a-fA-F]+)", query_output)

            ac_seconds = int(ac_match.group(1), 16) if ac_match else None
            dc_seconds = int(dc_match.group(1), 16) if dc_match else None

            time_values = [t for t in [ac_seconds, dc_seconds] if t is not None]
            return min(time_values) // 60 if time_values else None

        elif system == "Darwin":
            # ===== macOS: use pmset =====
            output = subprocess.check_output(["pmset", "-g", "custom"], text=True)

            ac_match = re.search(r" sleep\s+(\d+)", output)
            dc_match = re.search(r" sleep\s+(\d+)", output)

            ac_minutes = int(ac_match.group(1)) if ac_match else None
            dc_minutes = int(dc_match.group(1)) if dc_match else None

            time_values = [t for t in [ac_minutes, dc_minutes] if t is not None]
            return min(time_values) if time_values else None

        elif system == "Linux":
            # ===== Linux: try gsettings (GNOME) =====
            try:
                ac_timeout = subprocess.check_output(
                    ["gsettings", "get", "org.gnome.settings-daemon.plugins.power", "sleep-inactive-ac-timeout"],
                    text=True
                ).strip()
                ac_minutes = int(ac_timeout) // 60 if ac_timeout.isdigit() else None
            except Exception:
                ac_minutes = None

            try:
                dc_timeout = subprocess.check_output(
                    ["gsettings", "get", "org.gnome.settings-daemon.plugins.power", "sleep-inactive-battery-timeout"],
                    text=True
                ).strip()
                dc_minutes = int(dc_timeout) // 60 if dc_timeout.isdigit() else None
            except Exception:
                dc_minutes = None

            time_values = [t for t in [ac_minutes, dc_minutes] if t is not None]
            return min(time_values) if time_values else None

        else:
            return None

    except Exception as e:
        print(f"Error checking sleep timeout on {system}: {e}")
        return None

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

def data_changed(new_data, old_data):
    if not old_data:
        return True
    # Compare all fields except timestamp
    keys = set(new_data.keys()) - {"timestamp"}
    for key in keys:
        if new_data.get(key) != old_data.get(key):
            return True
    return False

def send_report(data):
    headers = {"x-api-key": API_KEY }
    try:
        resp = requests.post(API_ENDPOINT, json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            print("Report sent successfully.")
            return True
        else:
            print(f"Failed to send report. Status code: {resp.status_code}")
            return False
    except Exception as e:
        print(f"Error sending report: {e}")
        return False

def collect_data():
    data = {
        "machine_id": get_machine_id(),
        "os_type": platform.system(),
        "disk_encryption": check_disk_encryption(),
        "os_update_status": check_os_update_status(),
        "antivirus": check_antivirus(),
        "inactivity_sleep_minutes": check_inactivity_sleep(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return data

def main_loop():
    while True:
        print(f"Checking system status at {datetime.now()}")
        new_data = collect_data()
        old_data = load_cache()
        # print(new_data)
        if data_changed(new_data, old_data):
            print("Change detected, sending report...")
            if send_report(new_data):
                save_cache(new_data)
        else:
            print("No change detected. Skipping sending.")
        print(f"Sleeping for {CHECK_INTERVAL_MINUTES} minutes...\n")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
