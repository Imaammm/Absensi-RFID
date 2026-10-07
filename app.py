# -*- coding: utf-8 -*-
"""
Smart Attendance System: RFID + Face Recognition (2FA)
Production Kiosk & Admin Management Server
Tech Stack: Flask, Flask-SocketIO, OpenCV, PySerial, SQLite, TailwindCSS
"""

import os
import sys
import time
import io
import csv
import base64
import random
import threading
import datetime
from flask import Flask, render_template, Response, jsonify, request, send_file
from flask_socketio import SocketIO, emit

# Local Modules
import database as db
from face_engine import camera_manager, face_engine

# -------------------------------------------------------------------------
# INITIALIZATION & SETTINGS
# -------------------------------------------------------------------------
db.init_db()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-attendance-rfid-face-2fa-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

current_system_state = "idle"  # 'idle', 'scanning_face', 'success', 'denied'
state_lock = threading.Lock()
admin_listening_rfid = False

# Load Settings from DB
settings = db.get_all_settings()
auto_simulation_active = (settings.get("simulation_mode", "true").lower() == "true")
kiosk_attendance_mode = settings.get("kiosk_mode", "auto")  # 'auto', 'check_in', 'check_out'

# -------------------------------------------------------------------------
# VIDEO STREAM GENERATOR
# -------------------------------------------------------------------------
def generate_video_stream():
    while True:
        frame_bytes = camera_manager.get_display_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)

# -------------------------------------------------------------------------
# 2FA BIOMETRIC VERIFICATION PIPELINE
# -------------------------------------------------------------------------
def calculate_attendance_status(employee, scan_type):
    """Calculates whether attendance is on-time, late, or check-out based on settings."""
    now = datetime.datetime.now()
    cfg = db.get_all_settings()
    
    if scan_type == "check_out":
        return "pulang", "Absen Pulang Berhasil Tercatat"

    # For Check-In: check start time and grace period
    work_start_str = cfg.get("work_start_time", "08:00")
    tolerance_min = int(cfg.get("late_tolerance_minutes", "15"))

    try:
        sh, sm = map(int, work_start_str.split(":"))
        shift_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        late_cutoff = shift_start + datetime.timedelta(minutes=tolerance_min)

        if now <= late_cutoff:
            diff_min = int((now - shift_start).total_seconds() / 60)
            if diff_min > 0:
                note = f"Hadir (Dalam masa toleransi {diff_min} menit)"
            else:
                note = "Hadir Tepat Waktu"
            return "hadir", note
        else:
            late_by = int((now - shift_start).total_seconds() / 60)
            return "terlambat", f"Terlambat {late_by} menit (Batas toleransi: {work_start_str} +{tolerance_min}m)"
    except Exception as e:
        return "hadir", "Hadir Tercatat"

def execute_two_factor_auth(uid, requested_mode=None):
    """Executes the full 2FA workflow (RFID Lookup -> Face Scan -> DB Record)."""
    global current_system_state, kiosk_attendance_mode, admin_listening_rfid

    uid = uid.strip().upper()

    # If Admin is actively listening to register a card
    if admin_listening_rfid:
        socketio.emit('admin_rfid_detected', {'uid': uid})
        return

    with state_lock:
        if current_system_state != "idle":
            return
        current_system_state = "scanning_face"

    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%d %b %Y")

    # 1. Lookup employee from persistent SQLite database
    employee = db.get_employee_by_rfid(uid)

    # 2. Determine scan type (Check-In vs Check-Out)
    mode = requested_mode or kiosk_attendance_mode
    if mode == "auto":
        if employee:
            today_logs = db.get_today_employee_attendance(employee["id"])
            scan_type = "check_out" if len(today_logs) > 0 else "check_in"
        else:
            scan_type = "check_in"
    else:
        scan_type = mode

    emp_name = employee["name"] if employee else "Kartu Tidak Terdaftar"
    emp_dept = employee["department"] if employee else "-"
    emp_role = employee["role"] if employee else "-"

    # Notify camera overlay and frontend
    camera_manager.set_state("scanning_face", emp_name, uid)
    socketio.emit('rfid_scanned', {
        'uid': uid,
        'user_name': emp_name,
        'department': emp_dept,
        'role': emp_role,
        'scan_type': scan_type,
        'is_registered': (employee is not None),
        'timestamp': time_str
    })

    socketio.emit('status_update', {
        'state': 'scanning_face',
        'title': 'MEMINDAI WAJAH...',
        'subtitle': f"Kartu [{uid}] - {emp_name}. Harap menghadap ke kamera.",
        'uid': uid,
        'name': emp_name,
        'scan_type': scan_type
    })

    # 3. Simulate optical face alignment delay (1.5 seconds)
    time.sleep(1.5)

    # 4. Biometric Face Verification
    cfg = db.get_all_settings()
    threshold = float(cfg.get("face_threshold", "70.0"))

    if employee:
        emp_id = employee["id"]
        is_matched, confidence_str, bio_message = face_engine.verify_face_with_camera(
            target_emp_id=emp_id,
            threshold_confidence=threshold
        )

        if is_matched:
            result_state = "success"
            status, note = calculate_attendance_status(employee, scan_type)
            message = f"{note} • Verifikasi Biometrik Wajah Sukses"
        else:
            result_state = "denied"
            status = "ditolak"
            message = "Akses Ditolak: Wajah Tidak Cocok dengan Pemilik Kartu"
    else:
        result_state = "denied"
        status = "ditolak"
        confidence_str = "0.0%"
        message = f"Akses Ditolak: Kartu RFID [{uid}] Belum Terdaftar"

    # 5. Persist attendance to SQLite Database
    log_record = db.add_attendance_log(
        rfid_uid=uid,
        employee_name=emp_name,
        department=emp_dept,
        role=emp_role,
        scan_type=scan_type,
        status=status,
        confidence=confidence_str,
        notes=message,
        employee_id=employee["id"] if employee else None
    )

    with state_lock:
        current_system_state = result_state

    camera_manager.set_state(result_state, emp_name, uid)

    # Prepare detailed payload for frontend
    initials = "".join([part[0] for part in emp_name.split()[:2]]).upper() if employee else "??"
    attendance_payload = {
        'id': log_record['id'],
        'success': (result_state == 'success'),
        'state': result_state,
        'uid': uid,
        'name': emp_name,
        'department': emp_dept,
        'role': emp_role,
        'avatar_initials': initials,
        'time': time_str,
        'date': date_str,
        'scan_type': scan_type,
        'status': status,
        'confidence': confidence_str,
        'message': message
    }

    socketio.emit('attendance_result', attendance_payload)

    # 6. Display result for 3 seconds before resetting to IDLE
    time.sleep(3.0)

    with state_lock:
        current_system_state = "idle"

    camera_manager.set_state("idle")
    socketio.emit('status_update', {
        'state': 'idle',
        'title': 'MENUNGGU KARTU',
        'subtitle': 'Silakan tap kartu RFID Anda pada reader untuk absensi',
        'uid': None,
        'name': None
    })

# -------------------------------------------------------------------------
# BACKGROUND RFID READER & SIMULATION WORKER
# -------------------------------------------------------------------------
def rfid_worker_loop():
    global auto_simulation_active

    cfg = db.get_all_settings()
    sim_mode = (cfg.get("simulation_mode", "true").lower() == "true")
    port = cfg.get("serial_port", "COM3")
    baudrate = int(cfg.get("serial_baudrate", "9600"))

    # Physical Serial Port Reader
    if not sim_mode:
        try:
            import serial
            ser = serial.Serial(port, baudrate, timeout=1)
            print(f"[SERIAL] Connected to physical RFID hardware on {port} at {baudrate} baud.")
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line and len(line) >= 4:
                    print(f"[SERIAL] Physical RFID Read: {line}")
                    execute_two_factor_auth(line)
                time.sleep(0.05)
        except Exception as e:
            print(f"[SERIAL] Port error: {e}. Switching to simulation worker.")

    # Simulation loop: periodic auto-tap for testing
    print("[WORKER] RFID Background Simulator running.")
    while True:
        time.sleep(10)
        if auto_simulation_active and current_system_state == "idle":
            employees = db.get_all_employees(active_only=True)
            uids = [e["rfid_uid"] for e in employees if e.get("rfid_uid")]
            dummy_pool = uids + ["UNKNOWN_99X", "GUEST_404"]
            if dummy_pool:
                chosen = random.choice(dummy_pool)
                print(f"[SIMULATION] Auto-tap triggered: {chosen}")
                execute_two_factor_auth(chosen)

# -------------------------------------------------------------------------
# HTTP ROUTES
# -------------------------------------------------------------------------
@app.route('/')
def kiosk_view():
    cfg = db.get_all_settings()
    employees = db.get_all_employees(active_only=True)
    return render_template('index.html', employees=employees, settings=cfg)

@app.route('/admin')
def admin_view():
    cfg = db.get_all_settings()
    departments = db.get_departments_list()
    return render_template('admin.html', settings=cfg, departments=departments)

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_video_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# -------------------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------------------
@app.route('/api/stats/today', methods=['GET'])
def api_today_stats():
    return jsonify(db.get_today_stats())

@app.route('/api/employees', methods=['GET', 'POST'])
def api_employees():
    if request.method == 'GET':
        search = request.args.get('search', '').strip()
        dept = request.args.get('department', '').strip()
        employees = db.get_all_employees(search=search, department=dept, active_only=True)
        # Attach face sample counts
        for emp in employees:
            emp["face_samples"] = face_engine.count_enrolled_samples(emp["id"])
        return jsonify(employees)

    if request.method == 'POST':
        data = request.get_json() or {}
        nik = data.get('nik', '').strip()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        role = data.get('role', '').strip()
        rfid_uid = data.get('rfid_uid', '').strip()

        if not nik or not name or not department:
            return jsonify({'success': False, 'message': 'NIK, Nama, dan Departemen wajib diisi'}), 400

        try:
            emp_id = db.create_employee(nik, name, department, role, rfid_uid)
            return jsonify({'success': True, 'id': emp_id, 'message': f'Karyawan "{name}" berhasil ditambahkan!'})
        except Exception as e:
            err_msg = str(e)
            if 'employees.rfid_uid' in err_msg:
                return jsonify({'success': False, 'message': f'Gagal: UID Kartu "{rfid_uid}" sudah dipakai oleh karyawan lain! Gunakan kartu RFID yang berbeda.'}), 400
            elif 'employees.nik' in err_msg:
                return jsonify({'success': False, 'message': f'Gagal: NIK "{nik}" sudah terdaftar! Gunakan NIK yang berbeda.'}), 400
            return jsonify({'success': False, 'message': f'Gagal menambah karyawan: {err_msg}'}), 500

@app.route('/api/employees/<int:emp_id>', methods=['GET', 'PUT', 'DELETE'])
def api_employee_detail(emp_id):
    if request.method == 'GET':
        emp = db.get_employee_by_id(emp_id)
        if not emp:
            return jsonify({'error': 'Employee not found'}), 404
        emp["face_samples"] = face_engine.count_enrolled_samples(emp_id)
        return jsonify(emp)

    if request.method == 'PUT':
        data = request.get_json() or {}
        nik = data.get('nik', '').strip()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        role = data.get('role', '').strip()
        rfid_uid = data.get('rfid_uid', '').strip()

        try:
            db.update_employee(emp_id, nik, name, department, role, rfid_uid)
            return jsonify({'success': True, 'message': f'Data karyawan "{name}" berhasil diperbarui!'})
        except Exception as e:
            err_msg = str(e)
            if 'employees.rfid_uid' in err_msg:
                return jsonify({'success': False, 'message': f'Gagal: UID Kartu "{rfid_uid}" sudah dipakai oleh karyawan lain!'}), 400
            elif 'employees.nik' in err_msg:
                return jsonify({'success': False, 'message': f'Gagal: NIK "{nik}" sudah terdaftar!'}), 400
            return jsonify({'success': False, 'message': f'Gagal memperbarui data: {err_msg}'}), 500

    if request.method == 'DELETE':
        import shutil
        faces_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "faces", str(emp_id))
        if os.path.exists(faces_folder):
            shutil.rmtree(faces_folder, ignore_errors=True)
            face_engine.train_all_faces()
        db.delete_employee(emp_id)
        return jsonify({'success': True, 'message': 'Karyawan berhasil dihapus dan UID Kartu RFID telah dibebaskan!'})

@app.route('/api/employees/<int:emp_id>/enroll-face', methods=['POST'])
def api_enroll_face(emp_id):
    """Captures face from live camera or base64 image and updates LBPH model."""
    try:
        emp = db.get_employee_by_id(emp_id)
        if not emp:
            return jsonify({'success': False, 'message': f'Karyawan dengan ID {emp_id} tidak ditemukan'}), 404

        data = request.get_json(silent=True) or {}
        image_b64 = data.get('image_base64')

        if image_b64:
            # Decode base64 image
            try:
                import cv2
                import numpy as np
                header, encoded = image_b64.split(",", 1) if "," in image_b64 else ("", image_b64)
                img_bytes = base64.b64decode(encoded)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception as e:
                return jsonify({'success': False, 'message': f'Format gambar tidak valid: {e}'}), 400
        else:
            # Capture frame directly from active webcam
            img = camera_manager.get_raw_frame()

        if img is None:
            return jsonify({'success': False, 'message': 'Gagal mengambil gambar dari kamera'}), 500

        success, count = face_engine.enroll_face(emp_id, img)
        if success:
            db.set_face_enrolled(emp_id, count)
            return jsonify({
                'success': True,
                'message': f'Sampel wajah ke-{count} berhasil didaftarkan untuk {emp["name"]}!',
                'samples_count': count
            })
        return jsonify({'success': False, 'message': 'Wajah tidak terdeteksi. Posisikan wajah Anda tepat di dalam kotak kuning kamera.'}), 400
    except Exception as e:
        print(f"[ERROR] enroll-face failed: {e}")
        return jsonify({'success': False, 'message': f'Terjadi kesalahan sistem: {str(e)}'}), 500

@app.route('/api/attendance', methods=['GET'])
def api_attendance_logs():
    date = request.args.get('date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department')
    status = request.args.get('status')
    search = request.args.get('search')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    logs = db.get_attendance_logs(
        date=date,
        start_date=start_date,
        end_date=end_date,
        department=department,
        status=status,
        search=search,
        limit=limit,
        offset=offset
    )
    return jsonify(logs)

@app.route('/api/attendance/export', methods=['GET'])
def api_export_csv():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department')
    status = request.args.get('status')

    logs = db.get_attendance_logs(
        start_date=start_date,
        end_date=end_date,
        department=department,
        status=status,
        limit=5000
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Tanggal", "Waktu", "UID RFID", "Nama Karyawan", "Departemen", "Jabatan", "Tipe Absen", "Status", "Confidence", "Catatan"])

    for r in logs:
        writer.writerow([
            r["id"],
            r["date"],
            r["timestamp"],
            r["rfid_uid"],
            r["employee_name"],
            r.get("department", "-"),
            r.get("role", "-"),
            r.get("scan_type", "check_in"),
            r["status"].upper(),
            r.get("confidence", "-"),
            r.get("notes", "-")
        ])

    output.seek(0)
    filename = f"laporan_absensi_{datetime.date.today().isoformat()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    if request.method == 'GET':
        return jsonify(db.get_all_settings())

    if request.method == 'POST':
        data = request.get_json() or {}
        db.update_settings(data)

        # Apply simulation toggle immediately
        global auto_simulation_active, kiosk_attendance_mode
        if "simulation_mode" in data:
            auto_simulation_active = (str(data["simulation_mode"]).lower() == "true")
        if "kiosk_mode" in data:
            kiosk_attendance_mode = data["kiosk_mode"]
            socketio.emit('kiosk_mode_changed', {'mode': kiosk_attendance_mode})
        if "camera_index" in data:
            try:
                camera_manager.switch_camera(int(data["camera_index"]))
            except Exception as e:
                print(f"[CAM] Error switching camera index: {e}")

        return jsonify({'success': True, 'message': 'Pengaturan berhasil disimpan'})

@app.route('/api/departments', methods=['GET'])
def api_departments():
    return jsonify(db.get_departments_list())

@app.route('/api/rfid-tap', methods=['POST'])
def api_rfid_tap():
    """Endpoint untuk ESP32 (Wi-Fi HTTP) untuk mengirim UID kartu RFID."""
    data = request.get_json(silent=True) or {}
    uid = data.get('uid') or request.form.get('uid') or request.args.get('uid')
    if not uid:
        return jsonify({'success': False, 'message': 'UID RFID wajib diisi'}), 400

    uid = uid.strip().upper()
    if current_system_state == 'idle':
        threading.Thread(target=execute_two_factor_auth, args=(uid,), daemon=True).start()
        return jsonify({
            'success': True,
            'status': 'processing',
            'uid': uid,
            'message': f'UID {uid} diterima, verifikasi biometrik wajah dimulai.'
        })
    return jsonify({'success': False, 'status': 'busy', 'message': 'Sistem sedang memproses verifikasi'}), 429


# -------------------------------------------------------------------------
# SOCKETIO REAL-TIME EVENT HANDLERS
# -------------------------------------------------------------------------
@socketio.on('connect')
def handle_connect():
    emit('status_update', {
        'state': current_system_state,
        'title': 'MENUNGGU KARTU' if current_system_state == 'idle' else current_system_state.upper(),
        'subtitle': 'Silakan tap kartu RFID Anda pada reader untuk absensi'
    })
    emit('kiosk_mode_changed', {'mode': kiosk_attendance_mode})

@socketio.on('manual_rfid_trigger')
def handle_manual_rfid_trigger(data):
    uid = data.get('uid', 'E2000019')
    mode = data.get('mode', kiosk_attendance_mode)
    if current_system_state == 'idle':
        threading.Thread(target=execute_two_factor_auth, args=(uid, mode), daemon=True).start()
        return {'status': 'processing', 'uid': uid}
    return {'status': 'busy', 'message': 'Sistem sedang memproses verifikasi'}

@socketio.on('set_kiosk_mode')
def handle_set_kiosk_mode(data):
    global kiosk_attendance_mode
    kiosk_attendance_mode = data.get('mode', 'auto')
    db.update_settings({'kiosk_mode': kiosk_attendance_mode})
    emit('kiosk_mode_changed', {'mode': kiosk_attendance_mode}, broadcast=True)
    return {'mode': kiosk_attendance_mode}

@socketio.on('toggle_auto_simulation')
def handle_toggle_simulation(data):
    global auto_simulation_active
    auto_simulation_active = data.get('active', True)
    db.update_settings({'simulation_mode': str(auto_simulation_active).lower()})
    print(f"[SIMULATION] Auto-simulation state set to: {auto_simulation_active}")
    return {'auto_simulation_active': auto_simulation_active}

@socketio.on('set_admin_listening_rfid')
def handle_admin_listen_rfid(data):
    global admin_listening_rfid
    admin_listening_rfid = data.get('active', False)
    return {'admin_listening_rfid': admin_listening_rfid}

# -------------------------------------------------------------------------
# SERVER ENTRYPOINT
# -------------------------------------------------------------------------
if __name__ == '__main__':
    # Start background RFID worker thread
    bg_thread = threading.Thread(target=rfid_worker_loop, daemon=True)
    bg_thread.start()

    print("=" * 68)
    print(" SMART ATTENDANCE SYSTEM: RFID + BIOMETRIC FACE RECOGNITION 2FA")
    print(" Kiosk Terminal: http://127.0.0.1:5000/")
    print(" Admin Portal:   http://127.0.0.1:5000/admin")
    print("=" * 68)

    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
