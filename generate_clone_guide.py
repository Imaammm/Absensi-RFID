# -*- coding: utf-8 -*-
"""
Script to generate a beautifully styled Microsoft Word (.docx) document
for Cloning and Setting Up the Smart Attendance 2FA Repository on Another Device.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_clone_guide():
    doc = docx.Document()

    # Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colors
    COLOR_PRIMARY = RGBColor(14, 116, 144)      # Deep Cyan / Teal (#0E7490)
    COLOR_SECONDARY = RGBColor(30, 41, 59)     # Dark Slate (#1E293B)
    COLOR_ACCENT = RGBColor(2, 132, 199)       # Sky Blue (#0284C7)
    COLOR_MUTED = RGBColor(100, 116, 139)      # Muted Gray (#64748B)

    # Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(16)
    title_p.paragraph_format.space_after = Pt(6)
    title_run = title_p.add_run("PANDUAN LENGKAP: CLONE & SETUP PROYEK")
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_run = sub_p.add_run("Cara Mengunduh, Memasang, dan Menjalankan Sistem Absensi 2FA di Laptop / Komputer Lain")
    sub_run.font.name = "Calibri"
    sub_run.font.size = Pt(13)
    sub_run.font.color.rgb = COLOR_MUTED

    # Meta banner box
    meta_table = doc.add_table(rows=1, cols=1)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_cell = meta_table.cell(0, 0)
    meta_cell.width = Inches(6.5)
    set_cell_background(meta_cell, "F1F5F9")
    set_cell_margins(meta_cell, top=140, bottom=140, left=200, right=200)

    p_box = meta_cell.paragraphs[0]
    p_box.paragraph_format.space_after = Pt(0)
    r_box = p_box.add_run("📌 Repositori GitHub: https://github.com/Imaammm/Absensi-RFID.git\nPanduan ini dirancang agar siapapun (dosen, penguji, rekan tim, atau staf kantor) dapat menjalankan proyek ini dari nol di laptop baru hanya dalam 5 langkah mudah.")
    r_box.font.name = "Calibri"
    r_box.font.size = Pt(10)
    r_box.font.color.rgb = COLOR_SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    def add_section_heading(num_str, title_str):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        run_num = h.add_run(f"LANGKAH {num_str}: " if num_str.isdigit() else "")
        run_num.font.name = "Calibri"
        run_num.font.size = Pt(14)
        run_num.font.bold = True
        run_num.font.color.rgb = COLOR_PRIMARY
        
        run_txt = h.add_run(title_str)
        run_txt.font.name = "Calibri"
        run_txt.font.size = Pt(14)
        run_txt.font.bold = True
        run_txt.font.color.rgb = COLOR_SECONDARY
        return h

    def add_body_p(text, bold_prefix=None, italic=False, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = "Calibri"
            r_b.font.size = Pt(11)
            r_b.font.bold = True
            r_b.font.color.rgb = COLOR_SECONDARY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.italic = italic
        r.font.color.rgb = COLOR_SECONDARY
        return p

    def add_bullet_point(prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if prefix:
            r_b = p.add_run(prefix + " ")
            r_b.font.name = "Calibri"
            r_b.font.size = Pt(11)
            r_b.font.bold = True
            r_b.font.color.rgb = COLOR_PRIMARY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_SECONDARY
        return p

    def add_code_block(code_str):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "0F172A") # Dark Navy (#0F172A)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        cp = cell.paragraphs[0]
        cp.paragraph_format.space_after = Pt(0)
        r = cp.add_run(code_str)
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(56, 189, 248) # Cyan (#38BDF8)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # PRASYARAT
    # -------------------------------------------------------------
    add_section_heading("", "PRASYARAT SEBELUM MEMULAI DI PERANGKAT BARU")
    add_body_p("Sebelum melakukan proses pengunduhan, pastikan komputer/laptop baru sudah terpasang software dasar berikut:")
    add_bullet_point("1. Git for Windows:", "Unduh gratis di https://git-scm.com (klik Next sampai selesai).")
    add_bullet_point("2. Python (Versi 3.9 s/d 3.12):", "Unduh di https://www.python.org/downloads.\n⚠️ PENTING: Saat instalasi Python, centang kotak 'Add Python.exe to PATH' di layar paling pertama!")
    add_bullet_point("3. Web Browser Modern:", "Google Chrome, Microsoft Edge, atau Mozilla Firefox.")
    add_bullet_point("4. Port USB & Webcam:", "Webcam laptop internal atau webcam USB eksternal.")

    # -------------------------------------------------------------
    # LANGKAH 1: CLONE
    # -------------------------------------------------------------
    add_section_heading("1", "CLONE (MENGUNDUH) REPOSITORI DARI GITHUB")
    add_body_p(
        "Buka aplikasi Terminal (PowerShell / Command Prompt / Git Bash) di laptop baru, "
        "kemudian tentukan folder tempat Anda ingin menyimpan proyek (misal di Desktop atau D:\\Proyek). "
        "Lalu ketik perintah berikut:"
    )
    add_code_block("git clone https://github.com/Imaammm/Absensi-RFID.git\ncd Absensi-RFID")
    
    add_body_p(
        "Alternatif Tanpa Git (Download ZIP):\n"
        "Buka browser ke https://github.com/Imaammm/Absensi-RFID, klik tombol hijau '<> Code', "
        "pilih 'Download ZIP', lalu ekstrak folder ZIP tersebut ke komputer Anda."
    )

    # -------------------------------------------------------------
    # LANGKAH 2: BUAT VENV
    # -------------------------------------------------------------
    add_section_heading("2", "MEMBUAT VIRTUAL ENVIRONMENT (VENV) BARU")
    add_body_p(
        "Mengapa harus membuat venv baru? Karena folder venv sengaja tidak diunggah ke GitHub "
        "(agar ukuran file tidak berat dan mencegah file biner rusak di komputer yang berbeda). "
        "Ketik perintah ini di terminal:"
    )
    add_code_block("python -m venv venv")

    add_body_p("Setelah folder venv selesai dibuat, aktifkan lingkungan virtual tersebut dengan perintah:")
    add_code_block(".\\venv\\Scripts\\activate")

    add_body_p(
        "Tanda Berhasil: Di sebelah kiri teks baris terminal Anda akan muncul tanda (venv), "
        "misalnya: (venv) PS C:\\Users\\...\\Absensi-RFID>"
    )

    # -------------------------------------------------------------
    # LANGKAH 3: INSTALL DEPENDENCIES
    # -------------------------------------------------------------
    add_section_heading("3", "MENGINSTALL SELURUH LIBRARY YANG DIBUTUHKAN")
    add_body_p(
        "Seluruh paket library (OpenCV AI, Flask Web Server, Socket.IO, PySerial, python-docx) "
        "sudah dicatat rapi dalam file requirements.txt. Anda cukup menjalankan SATU perintah ini:"
    )
    add_code_block("pip install -r requirements.txt")
    add_body_p("Tunggu beberapa menit hingga proses download dan instalasi otomatis selesai.")

    # -------------------------------------------------------------
    # LANGKAH 4: HUBUNGKAN ALAT
    # -------------------------------------------------------------
    add_section_heading("4", "MENYAMBUNGKAN PERANGKAT KERAS (HARDWARE)")
    add_bullet_point("Koneksi USB ESP32:", "Colokkan kabel USB dari ESP32 ke laptop baru. Periksa nomor port COM-nya di 'Device Manager' Windows (misal: COM3, COM4, atau COM10).")
    add_bullet_point("Kamera Webcam:", "Jika memakai webcam eksternal, colokkan juga kabel USB-nya ke laptop.")
    add_bullet_point("Tanpa Hardware? (Mode Simulasi):", "Jika Anda belum membawa alat ESP32 fisik, sistem tetap 100% bisa diuji menggunakan tombol simulasi virtual di layar!")

    # -------------------------------------------------------------
    # LANGKAH 5: JALANKAN SERVER
    # -------------------------------------------------------------
    add_section_heading("5", "MENJALANKAN SERVER DAN MEMBUKA WEBSITE")
    add_body_p("Di terminal yang masih dalam kondisi (venv) aktif, ketik perintah berikut:")
    add_code_block("python app.py")

    add_body_p("Tunggu sebentar hingga muncul pemberitahuan di terminal:")
    add_code_block("====================================================================\n SMART ATTENDANCE SYSTEM: RFID + BIOMETRIC FACE RECOGNITION 2FA\n Kiosk Terminal: http://127.0.0.1:5000/\n Admin Portal:   http://127.0.0.1:5000/admin\n====================================================================")

    add_body_p("Sekarang buka browser (Google Chrome / Edge) dan buka alamat berikut:")
    add_bullet_point("Layar Absensi Karyawan:", "http://localhost:5000")
    add_bullet_point("Portal Manajemen HRD / Admin:", "http://localhost:5000/admin")

    # -------------------------------------------------------------
    # LANGKAH 6: KONFIGURASI AWAL
    # -------------------------------------------------------------
    add_section_heading("6", "PENYESUAIAN AWAL DI PORTAL ADMIN")
    add_body_p("Setelah halaman admin terbuka di http://localhost:5000/admin:")
    add_bullet_point("1. Masuk ke Tab Pengaturan Sistem:", "Ikon gerigi di menu navigasi atas.")
    add_bullet_point("2. Sesuaikan Port Serial (COM):", "Ganti nomor COM sesuai port ESP32 di laptop baru (contoh: COM4).")
    add_bullet_point("3. Sesuaikan Pilihan Kamera:", "Pilih 'Kamera 0 (Internal Laptop)' atau 'Kamera 1 (Webcam USB Eksternal)'.")
    add_bullet_point("4. Simpan:", "Klik tombol 'Simpan Konfigurasi Sistem'. Sistem langsung aktif sempurna!")

    # -------------------------------------------------------------
    # TROUBLESHOOTING PERANGKAT BARU
    # -------------------------------------------------------------
    add_section_heading("", "TIPS MENGATASI KENDALA DI KOMPUTER BARU")

    table_trouble = doc.add_table(rows=5, cols=3)
    table_trouble.alignment = WD_TABLE_ALIGNMENT.CENTER
    tb_headers = ["Pesan Error / Gejala", "Penyebab", "Solusi Mudah"]
    for i, h_text in enumerate(tb_headers):
        cell = table_trouble.cell(0, i)
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_trouble = [
        ("File .\\venv\\Scripts\\Activate.ps1 cannot be loaded because running scripts is disabled", "Kebijakan keamanan PowerShell Windows memblokir script.", "Jalankan perintah ini di PowerShell: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass lalu coba aktifkan venv kembali."),
        ("'python' is not recognized as an internal or external command", "Python belum ditambahkan ke System Environment Path.", "Install ulang Python dan pastikan mencentang kotak 'Add Python to PATH' saat install."),
        ("could not open port 'COM10'", "Nomor port COM di laptop baru berbeda, atau Arduino IDE masih membuka Serial Monitor.", "Tutup Serial Monitor di Arduino IDE, cek port COM di Device Manager, lalu perbarui di halaman Admin -> Pengaturan."),
        ("Layar kamera hitam / gelap gulita", "Izin akses kamera di Windows dimatikan, atau salah pilih nomor index kamera.", "Buka Windows Settings -> Privacy -> Camera -> izinkan akses kamera, atau ganti pilihan kamera di halaman Admin.")
    ]

    for row_idx, t_row in enumerate(data_trouble, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text_val in enumerate(t_row):
            cell = table_trouble.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Save Document
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PANDUAN_CLONE_DAN_SETUP_PERANGKAT_BARU.docx")
    doc.save(target_path)
    print(f"Clone guide successfully created at: {target_path}")

if __name__ == "__main__":
    create_clone_guide()
