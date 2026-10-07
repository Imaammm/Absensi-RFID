# 🏢 Sistem Absensi Cerdas Two-Factor Authentication (RFID + Biometric Face Recognition)
**Kiosk Terminal & Admin Management Portal (Flask + Flask-SocketIO + OpenCV LBPH + SQLite + TailwindCSS)**

---

## 📌 Gambaran Umum
Sistem ini merupakan solusi lengkap absensi karyawan berbasis **Two-Factor Authentication (2FA)** tingkat lanjut:
1. **Faktor 1 (What you have):** Kartu RFID fisik (MFRC522/Arduino via Serial COM) atau simulasi UID kartu karyawan.
2. **Faktor 2 (What you are):** Verifikasi biometrik wajah langsung melalui webcam secara real-time menggunakan **OpenCV Haar Cascade Face Detector** dan **LBPH (Local Binary Patterns Histograms) Face Recognizer**.

Sistem dilengkapi dengan **Database SQLite Persisten**, **Logika Jam Kerja (Masuk vs Pulang & Keterlambatan)**, **Voice Feedback (TTS Bahasa Indonesia)**, serta **Portal Manajemen Admin Terpadu**.

---

## 🚀 Fitur Utama

### 1. Terminal Kiosk Absensi (`http://localhost:5000/`)
- **Realtime Biometric Video Stream (`/video_feed`):**
  - Mengakses webcam fisik langsung via OpenCV (`VideoCapture(0)`).
  - Bounding box deteksi wajah interaktif dengan animasi pemindaian laser cyan.
  - Fallback otomatis ke *Hologram Silhouette Feed* jika webcam fisik tidak terpasang.
- **Logika Presensi Cerdas (Check-In vs Check-Out):**
  - Pilihan mode: `Auto (Cerdas)`, `Absen Masuk`, dan `Absen Pulang`.
  - Deteksi otomatis status: `Hadir (Tepat Waktu)`, `Terlambat (X menit)`, atau `Absen Pulang`.
- **Feedback Audio & Suara:**
  - Synthesizer nada konfirmasi (*chime*).
  - Voice Announcement Text-to-Speech (TTS) bahasa Indonesia: *"Selamat datang, Budi Santoso. Absen Masuk berhasil dicatat."*
- **Tabel Riwayat Kehadiran Hari Ini:**
  - Tersinkronisasi otomatis dengan SQLite database backend tanpa reload.

### 2. Portal Manajemen Admin (`http://localhost:5000/admin`)
- **Dashboard Ringkasan:** Statistik harian (Total Karyawan, Total Scan, Hadir, Terlambat, Ditolak) dan aktivitas absensi terbaru.
- **Master Data Karyawan:**
  - Tambah, Edit, dan Nonaktifkan karyawan.
  - Pasangkan UID Kartu RFID secara instan via listener scan kartu.
  - **Pendaftaran Wajah Biometrik (Face Enrollment):** Ambil foto wajah karyawan langsung melalui webcam atau unggah foto, dan model LBPH akan dilatih secara otomatis.
- **Laporan & Rekapitulasi Kehadiran:**
  - Filter rentang tanggal, departemen, status (Hadir, Terlambat, Pulang, Ditolak), dan pencarian nama/UID.
  - Tombol **Ekspor File CSV** langsung dari server.
- **Konfigurasi Sistem:**
  - Atur jam masuk kantor standar, batas toleransi keterlambatan (menit), jam pulang, ambang batas pengenalan wajah biometrik (%), mode simulasi, dan Serial COM Port.

---

## 🛠️ Struktur Direktori Proyek

```
rfid_face_attendance/
├── app.py                 # Server Flask, REST API, Socket.IO & RFID background thread
├── database.py            # SQLite schema, ORM helpers, seeder default karyawan
├── face_engine.py         # OpenCV Haar Cascade detection, LBPH training & verification
├── test_system.py         # Automated verification tests
├── requirements.txt       # Dependencies python terverifikasi
├── data/
│   ├── attendance.db      # Database SQLite persisten
│   ├── faces/             # Direktori dataset sampel wajah karyawan (per ID)
│   └── models/            # Model LBPH terlatih (face_model.yml)
├── templates/
│   ├── index.html         # Layar Kiosk Terminal interaktif
│   └── admin.html         # Portal Manajemen Admin lengkap
└── venv/                  # Python Virtual Environment
```

---

## ⚡ Panduan Menjalankan Aplikasi

### 1. Masuk ke Direktori Proyek
```powershell
cd "C:\Users\ACER NITRO\.gemini\antigravity\scratch\rfid_face_attendance"
```

### 2. Jalankan Virtual Environment & Server
```powershell
.\venv\Scripts\python.exe app.py
```

### 3. Akses Antarmuka Web
- **Layar Kiosk Absensi:** [http://localhost:5000](http://localhost:5000)
- **Portal Admin:** [http://localhost:5000/admin](http://localhost:5000/admin)

---

## ⚙️ Konfigurasi Hardware RFID Fisik (Opsional)
Jika menghubungkan modul hardware RFID fisik (Arduino Uno + RC522 MFRC522):
1. Buka Portal Admin di `http://localhost:5000/admin` ➔ Tab **Pengaturan Sistem**.
2. Matikan toggle **Mode Simulasi RFID**.
3. Masukkan port COM Arduino (misal: `COM3`) dan baudrate (misal: `9600`).
4. Klik **Simpan Konfigurasi Sistem**.
