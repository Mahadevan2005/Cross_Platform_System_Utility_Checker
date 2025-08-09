# Cross Platform System Utility Checker with Dashboard

A **cross-platform system monitoring tool** that collects key system health data from Windows, macOS, and Linux machines. It features a Python-based client utility, a FastAPI backend server for data collection and storage, and a React-based admin dashboard to visualize and filter machine statuses.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Architecture & Flow](#architecture--flow)  
- [Project Structure](#project-structure)  
- [Installation & Setup](#installation--setup)  
- [Usage](#usage)  
- [Sample Screenshots](#sample-screenshots)  
- [License](#license)  

---

## Project Overview

System Utility continuously monitors endpoint machines by collecting information such as disk encryption status, OS update status, antivirus presence, and inactivity sleep timeout. The client utility sends periodic reports to a backend server, which stores data and provides an API. An admin dashboard presents this data interactively with filters by OS and system health status.

---

## Architecture & Flow

1. **Utility-Client (Python)**  
   - Runs on each monitored machine (Windows/macOS/Linux).  
   - Collects system details (disk encryption, OS updates, antivirus status, sleep timeout).  
   - Detects changes and sends reports to backend API every 30 minutes.  

2. **Backend-Server (FastAPI + SQLite)**  
   - Accepts authenticated reports via REST API.  
   - Stores reports in SQLite database with timestamps.  
   - Provides endpoints to list machines and filter by OS and health status.

3. **Admin-Dashboard (React + MUI)**  
   - Fetches machine data from backend API.  
   - Displays machines in a sortable, paginated table.  
   - Filters machines by OS type and issue status (e.g., unencrypted disk, outdated OS).  
   - Highlights machines with potential issues for easy identification.

---

## Project Structure
```
/
├── utility-client/
│ └── sysutil.py # Python client utility for data collection and reporting
| └── requirements.txt
├── backend-server/
│ ├── main.py # FastAPI backend server
│ └── sysutil.db # SQLite database
  └── requirements.txt
├── admin-dashboard/
│ ├── src/
│ │ └── App.jsx # React admin dashboard component
│ ├── package.json # React project metadata & dependencies
│ └── ... # Other React files
├── README.md # Project documentation 
```
---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Mahadevan2005/Cross_Platform_System_Utility_Checker.git
```

### 2. Create & Activate Virtual Environment
- #### Create Virtual Environment
```bash
python -m venv venv
```
- #### Activate Virtual Environment
For Linux/macOS:
```
source venv/bin/activate
```
For Windows:
```
venv\\Scripts\\activate
```
### 3. Install Required Backend Package Dependencies
```bash
pip install -r requirements.txt
```
### 4. In terminal move into the directory "/backend-server" and start the server
```bash
cd backend-server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
### 5. In terminal move into the directory "utility-client" and start the process
```bash
cd utility-client
python sysutil.py
```
### 6. In terminal move into the directory "admin-dashboard" and start the frontend server
```bash
cd admin-dashboard
npm install
npm run dev
```

<hr>

## 📸 Screenshots
![Admin Dashboard](https://github.com/user-attachments/assets/216e5095-4ae7-4841-89b3-01318c9e00b3)

<h3 align="center">
Thank You ❤️
</h3>