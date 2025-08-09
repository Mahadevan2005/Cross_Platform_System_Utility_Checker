from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import datetime

API_KEY = "secret_key"  # Must match utility-client API_KEY

app = FastAPI(title="System Monitoring Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend URL like ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "sysutil.db"

# --- Database Init ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            os_type TEXT NOT NULL,
            disk_encryption BOOLEAN NOT NULL,
            os_current_version TEXT NOT NULL,
            os_latest_version TEXT NOT NULL,
            os_is_up_to_date BOOLEAN NOT NULL,
            antivirus_present BOOLEAN NOT NULL,
            antivirus_status TEXT NOT NULL,
            inactivity_sleep_minutes INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Pydantic Models ---

class OSUpdateStatus(BaseModel):
    current_version: str
    latest_version: str
    is_up_to_date: bool

class AntivirusStatus(BaseModel):
    present: bool
    status: str

class Report(BaseModel):
    machine_id: str
    os_type: str
    disk_encryption: bool
    os_update_status: OSUpdateStatus
    antivirus: AntivirusStatus
    inactivity_sleep_minutes: int
    timestamp: str

# --- API Key verification ---

def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

# --- Endpoints ---

@app.post("/api/report")
def receive_report(report: Report, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO reports (
            machine_id, os_type, disk_encryption,
            os_current_version, os_latest_version, os_is_up_to_date,
            antivirus_present, antivirus_status,
            inactivity_sleep_minutes, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report.machine_id,
        report.os_type,
        report.disk_encryption,
        report.os_update_status.current_version,
        report.os_update_status.latest_version,
        report.os_update_status.is_up_to_date,
        report.antivirus.present,
        report.antivirus.status,
        report.inactivity_sleep_minutes,
        report.timestamp
    ))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/machines")
def list_machines(os_type: Optional[str] = Query(None), issues: Optional[bool] = Query(False), x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    conn = get_db_connection()
    query = '''
        SELECT machine_id, os_type, disk_encryption,
               os_current_version, os_latest_version, os_is_up_to_date,
               antivirus_present, antivirus_status,
               inactivity_sleep_minutes, MAX(timestamp) as last_check_in
        FROM reports
        GROUP BY machine_id
    '''
    params = []
    results = conn.execute(query, params).fetchall()
    conn.close()

    machines = [dict(row) for row in results]

    # Filter by os_type
    if os_type:
        machines = [m for m in machines if m['os_type'].lower() == os_type.lower()]

    # Filter by issues flag
    if issues:
        def has_issue(m):
            return (not m['disk_encryption'] or
                    not m['os_is_up_to_date'] or
                    not m['antivirus_present'] or
                    m['inactivity_sleep_minutes'] > 10)
        machines = [m for m in machines if has_issue(m)]

    return {"machines": machines}
