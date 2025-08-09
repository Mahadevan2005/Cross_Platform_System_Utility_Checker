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
    """Check if OS is up to date."""
    system = platform.system()
    try:
        if system == "Windows":
            # Get current Windows version
            current_version = platform.version()
            # For demo, assume latest version is same as current (replace with real check)
            latest_version = current_version
            is_up_to_date = True
            return {
                "current_version": current_version,
                "latest_version": latest_version,
                "is_up_to_date": is_up_to_date
            }
        elif system == "Darwin":
            # macOS version
            current_version = subprocess.check_output(["sw_vers", "-productVersion"]).strip().decode()
            # For demo, assume latest is same (replace with API or web scrape)
            latest_version = current_version
            is_up_to_date = True
            return {
                "current_version": current_version,
                "latest_version": latest_version,
                "is_up_to_date": is_up_to_date
            }
        elif system == "Linux":
            # This varies greatly — for demo, return true and current version
            current_version = platform.release()
            latest_version = current_version
            is_up_to_date = True
            return {
                "current_version": current_version,
                "latest_version": latest_version,
                "is_up_to_date": is_up_to_date
            }
        else:
            return {
                "current_version": "unknown",
                "latest_version": "unknown",
                "is_up_to_date": False
            }
    except Exception:
        return {
            "current_version": "error",
            "latest_version": "error",
            "is_up_to_date": False
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

def check_inactivity_sleep():
    """Check inactivity sleep settings in minutes."""
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output(["powercfg", "/query"]).decode()
            # Find setting for sleep timeout on AC power (subgroup GUID: 238C9FA8-0AAD-41ED-83F4-97BE242C8F20, setting: 29F6C1DB-86DA-48C5-9FDB-F2B67B1F44DA)
            import re
            match = re.search(r"Sleep Timeout \(AC\):\s*Power Setting Index: 0x(\w+)", output)
            if match:
                val = int(match.group(1), 16)
                return val // 60  # seconds to minutes
            else:
                return 9999
        elif system == "Darwin":
            output = subprocess.check_output(["pmset", "-g"]).decode()
            import re
            match = re.search(r"sleep\s+(\d+)", output)
            if match:
                return int(match.group(1))
            else:
                return 9999
        elif system == "Linux":
            # For demo, assume 10 mins or less
            return 10
        else:
            return 9999
    except Exception:
        return 9999

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
