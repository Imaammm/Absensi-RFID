# -*- coding: utf-8 -*-
"""
Automated Verification Script for Smart Attendance 2FA System
Tests SQLite DB operations, Face Engine, and Flask REST API endpoints.
"""

import os
import sys
import unittest
import numpy as np
import cv2

# Import local modules
import database as db
from face_engine import face_engine, camera_manager
from app import app

class TestAttendanceSystem(unittest.TestCase):
    def setUp(self):
        db.init_db()
        self.client = app.test_client()

    def test_database_employees(self):
        employees = db.get_all_employees()
        self.assertGreaterEqual(len(employees), 1, "At least 1 active employee should exist")
        
        # Test lookup by RFID of first employee
        first_emp = employees[0]
        if first_emp.get("rfid_uid"):
            found = db.get_employee_by_rfid(first_emp["rfid_uid"])
            self.assertIsNotNone(found)
            self.assertEqual(found["id"], first_emp["id"])
        print("[TEST OK] Database Employee lookup by RFID verified.")

    def test_attendance_logging(self):
        log = db.add_attendance_log(
            rfid_uid="E2000019",
            employee_name="Budi Santoso",
            department="IT & Engineering",
            role="Senior Software Engineer",
            scan_type="check_in",
            status="hadir",
            confidence="96.5%",
            notes="Unit Test Log Entry"
        )
        self.assertIsNotNone(log["id"])
        
        logs = db.get_attendance_logs(limit=5)
        self.assertTrue(any(l["rfid_uid"] == "E2000019" for l in logs))
        print("[TEST OK] Attendance Logging to SQLite verified.")

    def test_face_engine_synthetic_or_webcam(self):
        raw = camera_manager.get_raw_frame()
        self.assertIsNotNone(raw)
        self.assertEqual(raw.shape[2], 3)
        
        # Test synthetic face image enrollment
        dummy_face = np.full((300, 300, 3), 128, dtype=np.uint8)
        cv2.circle(dummy_face, (150, 130), 60, (200, 200, 200), -1)
        cv2.circle(dummy_face, (130, 120), 8, (50, 50, 50), -1)
        cv2.circle(dummy_face, (170, 120), 8, (50, 50, 50), -1)
        cv2.ellipse(dummy_face, (150, 160), (25, 12), 0, 0, 180, (50, 50, 50), -1)
        
        success, count = face_engine.enroll_face(emp_id=1, image_bgr=dummy_face)
        self.assertTrue(success)
        self.assertGreaterEqual(count, 1)
        print(f"[TEST OK] Face Engine Enrollment verified (Sample #{count}).")

    def test_api_endpoints(self):
        # 1. Stats endpoint
        res = self.client.get('/api/stats/today')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_scans", data)
        self.assertIn("hadir", data)

        # 2. Employees endpoint
        res = self.client.get('/api/employees')
        self.assertEqual(res.status_code, 200)
        emps = res.get_json()
        self.assertIsInstance(emps, list)

        # 3. Attendance logs endpoint
        res = self.client.get('/api/attendance')
        self.assertEqual(res.status_code, 200)

        # 4. Settings endpoint
        res = self.client.get('/api/settings')
        self.assertEqual(res.status_code, 200)
        settings = res.get_json()
        self.assertIn("work_start_time", settings)
        print("[TEST OK] REST API endpoints verified successfully.")

if __name__ == '__main__':
    unittest.main()
