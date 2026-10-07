# -*- coding: utf-8 -*-
"""
Database Management Module for Smart Attendance System (SQLite)
Handles schema initialization, CRUD for employees, attendance logs, and system settings.
Thread-safe and WAL-mode enabled for concurrent web & background reader operations.
"""

import os
import sqlite3
import datetime
import threading

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "attendance.db")

db_lock = threading.Lock()

def get_db_connection():
    """Returns a SQLite connection configured with Row factory and timeout."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
    except Exception:
        pass
    return conn

def init_db():
    """Initializes tables and seeds default data if empty."""
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 1. Employees Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nik TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL,
                rfid_uid TEXT UNIQUE,
                photo_url TEXT,
                face_enrolled INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 2. Attendance Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                rfid_uid TEXT NOT NULL,
                employee_name TEXT NOT NULL,
                department TEXT,
                role TEXT,
                timestamp TEXT NOT NULL,
                date TEXT NOT NULL,
                scan_type TEXT DEFAULT 'check_in', -- 'check_in' or 'check_out'
                status TEXT NOT NULL,              -- 'hadir', 'terlambat', 'pulang', 'ditolak'
                confidence TEXT,
                verification_mode TEXT DEFAULT 'rfid_face',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE SET NULL
            )
            """)

            # 3. System Settings Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT
            )
            """)

            # Default Settings
            default_settings = [
                ("work_start_time", "08:00", "Jam masuk standar kantor (HH:MM)"),
                ("late_tolerance_minutes", "15", "Toleransi keterlambatan dalam menit"),
                ("work_end_time", "17:00", "Jam pulang standar kantor (HH:MM)"),
                ("simulation_mode", "true", "Mode simulasi RFID (true/false)"),
                ("serial_port", "COM3", "Port Serial RFID Hardware"),
                ("serial_baudrate", "9600", "Baudrate Port Serial"),
                ("face_threshold", "60", "Ambang batas confidence minimal pengenalan wajah (%)"),
                ("camera_index", "0", "Index perangkat webcam (0=internal, 1=eksternal USB)"),
                ("kiosk_mode", "auto", "Mode absensi kiosk: auto, check_in, check_out")
            ]

            for key, val, desc in default_settings:
                cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value, description)
                VALUES (?, ?, ?)
                """, (key, val, desc))

            # 4. Seed Default Employees if table is empty
            cursor.execute("SELECT COUNT(*) as cnt FROM employees")
            if cursor.fetchone()["cnt"] == 0:
                default_employees = [
                    ("EMP001", "Budi Santoso", "IT & Engineering", "Senior Software Engineer", "E2000019", 1),
                    ("EMP002", "Siti Rahma", "Human Resources", "People Operations Lead", "A134F90B", 1),
                    ("EMP003", "Dimas Pratama", "Finance & Accounting", "Financial Analyst", "8833DC1A", 1),
                    ("EMP004", "Anisa Putri", "Product & UI/UX Design", "Lead UI/UX Designer", "C4B1278E", 1)
                ]
                cursor.executemany("""
                INSERT INTO employees (nik, name, department, role, rfid_uid, face_enrolled)
                VALUES (?, ?, ?, ?, ?, ?)
                """, default_employees)

            conn.commit()
        finally:
            conn.close()

# -------------------------------------------------------------------------
# EMPLOYEE CRUD HELPERS
# -------------------------------------------------------------------------
def get_all_employees(search=None, department=None, active_only=True):
    with db_lock:
        conn = get_db_connection()
        try:
            query = "SELECT * FROM employees WHERE 1=1"
            params = []

            if active_only:
                query += " AND is_active = 1"
            if department and department != "ALL":
                query += " AND department = ?"
                params.append(department)
            if search:
                query += " AND (name LIKE ? OR nik LIKE ? OR rfid_uid LIKE ?)"
                term = f"%{search}%"
                params.extend([term, term, term])

            query += " ORDER BY name ASC"
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

def get_employee_by_id(emp_id):
    with db_lock:
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT * FROM employees WHERE id = ?", (emp_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

def get_employee_by_rfid(rfid_uid):
    if not rfid_uid:
        return None
    with db_lock:
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT * FROM employees WHERE UPPER(rfid_uid) = UPPER(?) AND is_active = 1", (rfid_uid.strip(),)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

def create_employee(nik, name, department, role, rfid_uid=None):
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            rfid = rfid_uid.strip().upper() if (rfid_uid and str(rfid_uid).strip()) else None
            cursor.execute("""
            INSERT INTO employees (nik, name, department, role, rfid_uid)
            VALUES (?, ?, ?, ?, ?)
            """, (nik.strip(), name.strip(), department.strip(), role.strip(), rfid))
            emp_id = cursor.lastrowid
            conn.commit()
            return emp_id
        finally:
            conn.close()

def update_employee(emp_id, nik, name, department, role, rfid_uid=None, is_active=1):
    with db_lock:
        conn = get_db_connection()
        try:
            rfid = rfid_uid.strip().upper() if (rfid_uid and str(rfid_uid).strip()) else None
            conn.execute("""
            UPDATE employees 
            SET nik = ?, name = ?, department = ?, role = ?, rfid_uid = ?, is_active = ?
            WHERE id = ?
            """, (nik.strip(), name.strip(), department.strip(), role.strip(), rfid, is_active, emp_id))
            conn.commit()
        finally:
            conn.close()

def set_face_enrolled(emp_id, enrolled=1):
    with db_lock:
        conn = get_db_connection()
        try:
            conn.execute("UPDATE employees SET face_enrolled = ? WHERE id = ?", (enrolled, emp_id))
            conn.commit()
        finally:
            conn.close()

def delete_employee(emp_id):
    with db_lock:
        conn = get_db_connection()
        try:
            # Delete employee record to free UID and NIK for reuse
            conn.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
            conn.commit()
        finally:
            conn.close()

# -------------------------------------------------------------------------
# ATTENDANCE LOG HELPERS
# -------------------------------------------------------------------------
def add_attendance_log(rfid_uid, employee_name, department, role, scan_type, status, confidence, notes=None, employee_id=None):
    with db_lock:
        conn = get_db_connection()
        try:
            now = datetime.datetime.now()
            timestamp_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%Y-%m-%d")

            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO attendance_logs 
            (employee_id, rfid_uid, employee_name, department, role, timestamp, date, scan_type, status, confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (employee_id, rfid_uid, employee_name, department, role, timestamp_str, date_str, scan_type, status, confidence, notes))
            log_id = cursor.lastrowid
            conn.commit()

            return {
                "id": log_id,
                "employee_id": employee_id,
                "rfid_uid": rfid_uid,
                "name": employee_name,
                "department": department,
                "role": role,
                "time": timestamp_str,
                "date": now.strftime("%d %b %Y"),
                "scan_type": scan_type,
                "status": status,
                "confidence": confidence,
                "notes": notes
            }
        finally:
            conn.close()

def get_attendance_logs(date=None, start_date=None, end_date=None, department=None, status=None, search=None, limit=100, offset=0):
    with db_lock:
        conn = get_db_connection()
        try:
            query = "SELECT * FROM attendance_logs WHERE 1=1"
            params = []

            if date:
                query += " AND date = ?"
                params.append(date)
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            if department and department != "ALL":
                query += " AND department = ?"
                params.append(department)
            if status and status != "ALL":
                query += " AND status = ?"
                params.append(status)
            if search:
                query += " AND (employee_name LIKE ? OR rfid_uid LIKE ?)"
                term = f"%{search}%"
                params.extend([term, term])

            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

def get_today_employee_attendance(employee_id):
    """Returns today's logs for a specific employee to determine check-in vs check-out."""
    if not employee_id:
        return []
    with db_lock:
        conn = get_db_connection()
        try:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            rows = conn.execute("""
            SELECT * FROM attendance_logs 
            WHERE employee_id = ? AND date = ? AND status != 'ditolak'
            ORDER BY id ASC
            """, (employee_id, today_str)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

def get_today_stats():
    with db_lock:
        conn = get_db_connection()
        try:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")

            total = conn.execute("SELECT COUNT(*) as c FROM attendance_logs WHERE date = ?", (today_str,)).fetchone()["c"]
            hadir = conn.execute("SELECT COUNT(*) as c FROM attendance_logs WHERE date = ? AND status = 'hadir'", (today_str,)).fetchone()["c"]
            terlambat = conn.execute("SELECT COUNT(*) as c FROM attendance_logs WHERE date = ? AND status = 'terlambat'", (today_str,)).fetchone()["c"]
            pulang = conn.execute("SELECT COUNT(*) as c FROM attendance_logs WHERE date = ? AND status = 'pulang'", (today_str,)).fetchone()["c"]
            ditolak = conn.execute("SELECT COUNT(*) as c FROM attendance_logs WHERE date = ? AND status = 'ditolak'", (today_str,)).fetchone()["c"]
            total_employees = conn.execute("SELECT COUNT(*) as c FROM employees WHERE is_active = 1").fetchone()["c"]

            return {
                "total_scans": total,
                "hadir": hadir,
                "terlambat": terlambat,
                "pulang": pulang,
                "ditolak": ditolak,
                "total_employees": total_employees,
                "date": datetime.datetime.now().strftime("%d %B %Y")
            }
        finally:
            conn.close()

# -------------------------------------------------------------------------
# SETTINGS HELPERS
# -------------------------------------------------------------------------
def get_all_settings():
    with db_lock:
        conn = get_db_connection()
        try:
            rows = conn.execute("SELECT key, value, description FROM settings").fetchall()
            return {row["key"]: row["value"] for row in rows}
        finally:
            conn.close()

def update_settings(settings_dict):
    with db_lock:
        conn = get_db_connection()
        try:
            for k, v in settings_dict.items():
                conn.execute("UPDATE settings SET value = ? WHERE key = ?", (str(v), k))
            conn.commit()
        finally:
            conn.close()

def get_departments_list():
    with db_lock:
        conn = get_db_connection()
        try:
            rows = conn.execute("SELECT DISTINCT department FROM employees WHERE is_active = 1 ORDER BY department ASC").fetchall()
            return [r["department"] for r in rows if r["department"]]
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()
    print("[DB INIT] Database initialized successfully at:", DB_PATH)
