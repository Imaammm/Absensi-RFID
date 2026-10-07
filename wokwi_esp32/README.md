# 📟 Panduan Simulasi ESP32 RFID di Wokwi

Direktori ini berisi kode lengkap firmware dan rangkaian untuk menjalankan simulasi **ESP32 RFID Reader Terminal** di [Wokwi.com](https://wokwi.com).

---

## 🏗️ Arsitektur ESP32 ke Laptop / Server Flask

```
[ESP32 Terminal Fisik / Wokwi]
   ├── Layar OLED I2C (128x64) -> Menampilkan status "Tap Kartu..."
   ├── Buzzer & LED           -> Nada konfirmasi & indikator
   └── 4 Tombol Kartu RFID    -> Simulasi Tap Kartu Karyawan
        │
        ├── (Jalur 1: USB Serial COM Port) ──> Serial.println(UID) ──> Flask (app.py)
        │
        └── (Jalur 2: Wi-Fi HTTP POST)      ──> POST /api/rfid-tap ──> Flask (app.py)
```

ESP32 mengirimkan UID kartu melalui **dua jalur sekaligus**:
1. **Serial USB (`COM Port`):** Jika ESP32 dicolok via kabel USB ke laptop, `app.py` langsung membacanya via `pyserial`.
2. **Wi-Fi HTTP (`/api/rfid-tap`):** ESP32 mengirim JSON `{ "uid": "E2000019" }` lewat jaringan Wi-Fi lokal, memicu Kiosk untuk langsung memindai wajah biometrik.

---

## ⚡ Cara Menjalankan di Wokwi (Hanya 1 Menit)

1. Buka browser dan kunjungi: **[https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32)**
2. Pada tab editor kode **`sketch.ino`**:
   - Hapus semua isi kodenya.
   - Buka file [`wokwi_esp32/sketch.ino`](file:///c:/Users/ACER%20NITRO/.gemini/antigravity/scratch/rfid_face_attendance/wokwi_esp32/sketch.ino), copy semua isinya, dan paste ke tab `sketch.ino` di Wokwi.
3. Pada tab **`diagram.json`**:
   - Hapus isinya.
   - Buka file [`wokwi_esp32/diagram.json`](file:///c:/Users/ACER%20NITRO/.gemini/antigravity/scratch/rfid_face_attendance/wokwi_esp32/diagram.json), copy semua isinya, dan paste ke tab `diagram.json` di Wokwi.
4. Pada tab **`Library Manager`** (ikon buku di sebelah kiri atau file `libraries.txt`):
   - Tambahkan 3 library ini:
     - `Adafruit SSD1306`
     - `Adafruit GFX Library`
     - `ArduinoJson`
5. Klik tombol hijau **`▶ Play / Start Simulation`**.

---

## 🎮 Cara Menguji di Wokwi

1. Perhatikan layar OLED: Status akan menampilkan *"Silakan Tap Kartu..."*.
2. Tekan salah satu tombol di sebelah kiri ESP32:
   - **Tombol Biru (1):** Tap Kartu Budi Santoso (`E2000019`)
   - **Tombol Hijau (2):** Tap Kartu Siti Rahma (`A134F90B`)
   - **Tombol Oranye (3):** Tap Kartu Dimas Pratama (`8833DC1A`)
   - **Tombol Merah (4):** Tap Kartu Asing (`UNKNOWN_99X`)
3. Buzzer akan berbunyi beep ganda, layar OLED menampilkan detail kartu yang di-tap, dan UID dicetak ke Serial Monitor Wokwi.

---

## 🔌 Cara Pindah ke Hardware Fisik (ESP32 + RC522 Asli)

Jika nanti Anda menghubungkan modul reader fisik **MFRC522**, hubungkan pin berikut:

| Pin Modul RC522 | Pin ESP32 (SPI) |
| :--- | :--- |
| **SDA (SS)** | GPIO 5 |
| **SCK** | GPIO 18 |
| **MOSI** | GPIO 23 |
| **MISO** | GPIO 19 |
| **RST** | GPIO 22 |
| **GND** | GND |
| **3.3V** | 3V3 (Jangan 5V!) |

Kode untuk membaca kartu fisik sudah disertakan di bagian komentar bawah file `sketch.ino`.
