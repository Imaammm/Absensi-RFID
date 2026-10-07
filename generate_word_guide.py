# -*- coding: utf-8 -*-
"""
Script to generate a beautifully styled Microsoft Word (.docx) document
for the Smart Attendance 2FA System Guide.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets cell background color."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets padding inside table cells."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()

    # Set Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles
    COLOR_PRIMARY = RGBColor(14, 116, 144)      # Deep Cyan / Teal (#0E7490)
    COLOR_SECONDARY = RGBColor(30, 41, 59)     # Dark Slate (#1E293B)
    COLOR_ACCENT = RGBColor(2, 132, 199)       # Sky Blue (#0284C7)
    COLOR_MUTED = RGBColor(100, 116, 139)      # Muted Gray (#64748B)

    # -------------------------------------------------------------
    # COVER / HEADER TITLE
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(6)
    title_run = title_p.add_run("BUKU PANDUAN & DOKUMENTASI LENGKAP")
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_run = sub_p.add_run("Sistem Absensi Cerdas 2FA: Kartu RFID (ESP32) & Pengenalan Wajah AI (OpenCV)")
    sub_run.font.name = "Calibri"
    sub_run.font.size = Pt(14)
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
    r_box = p_box.add_run("💡 Panduan Komprehensif: Ditulis dengan bahasa yang ramah untuk orang awam, dilengkapi analogi dunia nyata, cara kerja AI, diagram alur, hingga panduan teknis operasional.")
    r_box.font.name = "Calibri"
    r_box.font.size = Pt(10.5)
    r_box.font.color.rgb = COLOR_SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # Helper function for Section Headings
    def add_section_heading(num_str, title_str):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
        h.paragraph_format.keep_with_next = True
        run_num = h.add_run(f"{num_str}. ")
        run_num.font.name = "Calibri"
        run_num.font.size = Pt(16)
        run_num.font.bold = True
        run_num.font.color.rgb = COLOR_PRIMARY
        
        run_txt = h.add_run(title_str)
        run_txt.font.name = "Calibri"
        run_txt.font.size = Pt(16)
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

    def add_callout(quote_text, bg_hex="EFF6FF", border_color="0284C7"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        cp = cell.paragraphs[0]
        cp.paragraph_format.space_after = Pt(0)
        r = cp.add_run(quote_text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.italic = True
        r.font.color.rgb = COLOR_SECONDARY
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # 1. PENGANTAR SEDERHANA
    # -------------------------------------------------------------
    add_section_heading("1", "PENGANTAR SEDERHANA: APA ITU SISTEM INI?")
    add_body_p(
        "Bayangkan di depan pintu masuk kantor atau sekolah Anda ditempatkan seorang satpam digital yang super teliti, "
        "tidak pernah mengantuk, dan tidak bisa disuap. Ketika ada seorang karyawan yang ingin mencatat kehadiran:"
    )
    add_bullet_point("Langkah 1:", "Karyawan menempelkan kartu identitas fisiknya ke mesin pembaca (Tap Kartu RFID).")
    add_bullet_point("Langkah 2:", "Satpam digital melihat data di kartu tersebut, lalu menatap wajah orang yang berdiri di depannya melalui kamera.")
    add_bullet_point("Langkah 3:", "Jika orang yang menempelkan kartu benar-benar pemilik sah kartu, komputer tersenyum, menyapa dengan suara ramah berbahasa Indonesia: 'Selamat datang, Muhammad Ucup!', dan langsung mencatat waktu hadirnya.")
    add_bullet_point("Langkah 4:", "Jika ternyata kartu itu adalah kartu titipan milik temannya yang bolos, komputer langsung menolak tegas: 'Wajah Anda tidak cocok dengan pemilik kartu!'")
    
    add_callout("Prinsip Utama: Menempelkan kartu saja tidak cukup. Orangnya harus hadir secara fisik di depan kamera agar kehadiran diakui!")

    # -------------------------------------------------------------
    # 2. MASALAH NYATA
    # -------------------------------------------------------------
    add_section_heading("2", "MASALAH NYATA: MENGAPA SISTEM INI DICIPTAKAN?")
    add_body_p("Sebelum adanya sistem ini, metode absensi lama di kantor memiliki berbagai celah kelemahan yang merugikan perusahaan:")

    table_masalah = doc.add_table(rows=4, cols=3)
    table_masalah.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Metode Lama", "Kelemahan Nyata di Lapangan", "Solusi Sistem 2FA Ini"]
    for i, h_text in enumerate(headers):
        cell = table_masalah.cell(0, i)
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_masalah = [
        ("Kertas Tanda Tangan Manual", "Sangat mudah dipalsukan, rekan kerja bisa menandatangani nama temannya (titip absen), kertas mudah sobek/rusak, dan merepotkan saat rekap bulanan.", "100% Digital: Data tersimpan seketika di database komputer, tidak bisa dipalsukan, dan siap diunduh ke Excel."),
        ("Kartu Biasa (Hanya RFID)", "Karyawan yang bangun kesiangan bisa menitipkan kartunya kepada rekannya untuk di-tap kan (praktik Buddy Punching).", "Wajib Verifikasi Wajah: Walaupun membawa kartu teman, sistem akan memblokir karena wajah di kamera tidak cocok."),
        ("Sidik Jari (Fingerprint)", "Kaca sensor sering kotor oleh minyak/debu sehingga gagal membaca jari basah, memicu antrean panjang, dan tidak higienis karena disentuh bergantian.", "Tanpa Sentuh (Touchless): Cukup dekatkan kartu tanpa menempel penuh, dan wajah dipindai dari jarak jauh tanpa menyentuh layar.")
    ]

    for row_idx, data_row in enumerate(data_masalah, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text_val in enumerate(data_row):
            cell = table_masalah.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(10)
            r.font.color.rgb = COLOR_SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------
    # 3. KONSEP 2FA
    # -------------------------------------------------------------
    add_section_heading("3", "KONSEP '2FA': KEAMANAN LAPIS GANDA DENGAN ANALOGI ATM")
    add_body_p(
        "Istilah 2FA (Two-Factor Authentication) terdengar sangat teknis, namun sebenarnya sudah biasa kita temui "
        "dalam kehidupan sehari-hari saat mengambil uang di mesin ATM:"
    )
    add_bullet_point("Faktor 1 (Benda yang Anda Miliki / What You Have):", "Di ATM adalah Kartu ATM fisik. Pada sistem absensi ini adalah Kartu / Gantungan Kunci RFID fisik.")
    add_bullet_point("Faktor 2 (Ciri Diri Anda Sendiri / Who You Are):", "Di ATM adalah nomor PIN rahasia. Pada sistem ini adalah Wajah Biometrik Anda sendiri.")
    
    add_body_p(
        "Kesimpulan Keamanan: Jika ada orang yang menemukan kartu Anda terjatuh di jalan, orang tersebut TIDAK BISA "
        "menggunakannya untuk absen, karena wajahnya tidak cocok dengan data Anda!",
        italic=True
    )

    # -------------------------------------------------------------
    # 4. MENGENAL ALAT & KOMPONEN
    # -------------------------------------------------------------
    add_section_heading("4", "MENGENAL ALAT DAN KOMPONEN SISTEM (ANALOGI PERAN)")
    add_body_p("Agar mudah dibayangkan, mari kita kenali peran dari setiap komponen seperti sebuah tim kerja:")

    add_bullet_point("1. Kartu RFID & Gantungan Biru (Tag RFID):", "Berperan sebagai 'KTP Elektronik'. Di dalam kartu tipis ini tertanam chip dan antena mikro tanpa baterai. Saat didekatkan ke sensor, kartu memancarkan nomor seri unik (UID, misal: 6974F903).")
    add_bullet_point("2. Modul RFID RC522 (Papan Biru Kecil):", "Berperan sebagai 'Telinga Pendengar Kartu'. Menggunakan gelombang radio frekuensi 13.56 MHz untuk mendeteksi nomor UID kartu dalam jarak 1–3 cm.")
    add_bullet_point("3. Mikrokontroler ESP32:", "Berperan sebagai 'Kurir Cepat'. Komputer mikro mini seukuran jari tangan yang bertugas mengambil kode UID dari sensor RC522 lalu mengirimkannya lewat kabel USB ke laptop server dalam hitungan mikrodetik.")
    add_bullet_point("4. Kamera Webcam (Laptop / USB Eksternal):", "Berperan sebagai 'Mata Pengawas'. Mengambil video wajah orang yang sedang berdiri di depan alat absensi.")
    add_bullet_point("5. Komputer Server (Program Python app.py):", "Berperan sebagai 'Komandan Utama / Manajer'. Mengkoordinasikan segalanya: menerima data dari ESP32, memerintahkan AI menganalisis kamera, mencatat jam masuk/pulang, dan memperbarui tampilan web.")
    add_bullet_point("6. Mesin Pengenal Wajah AI (OpenCV di face_engine.py):", "Berperan sebagai 'Detektif Biometrik'. Mengukur kontur dan ciri unik wajah dari kamera, lalu mencocokkannya dengan arsip foto wajah karyawan.")
    add_bullet_point("7. Database SQLite (attendance.db):", "Berperan sebagai 'Buku Catatan Kehadiran Abadi'. Menyimpan daftar seluruh karyawan, jam kedatangan, keterlambatan, dan riwayat absensi secara aman dan permanen.")

    # -------------------------------------------------------------
    # 5. CERITA SIMULASI
    # -------------------------------------------------------------
    add_section_heading("5", "CERITA SIMULASI: BAGAIMANA SISTEM BEKERJA DARI DETIK KE DETIK?")
    
    add_body_p("Skenario 1: Karyawan Absen Sendiri (Proses Sukses)", bold_prefix="🟢 ")
    add_body_p(
        "Pukul 07.50 WIB, Muhammad Ucup tiba di kantor. Layar tablet di meja resepsionis berada dalam mode Standby. "
        "Ucup mendekatkan kartu gantungan birunya ke sensor RFID.\n"
        "• Detik 0.1: Sensor membaca kode UID 6974F903. ESP32 mengirimkannya ke komputer server.\n"
        "• Detik 0.2: Komputer memeriksa database: 'Kartu ini milik Muhammad Ucup dari divisi Polisi/Sappol!'\n"
        "• Detik 0.3: Layar berubah warna biru dengan pesan: 'MEMINDAI WAJAH... Harap menatap kamera'. Kotak pemindai muncul di wajah Ucup.\n"
        "• Detik 0.8: Kamera mengambil 6 frame secara cepat. AI mencocokkan wajah dan menghasilkan skor 92.4% (Sangat Cocok).\n"
        "• Detik 1.2: Komputer membandingkan jam saat itu (07.50) dengan jam masuk kantor (08.00). Status: Hadir Tepat Waktu.\n"
        "• Detik 1.5: Layar menyala hijau dengan tanda centang besar. Komputer bersuara ramah bahasa Indonesia:\n"
        "   \"Selamat datang, Muhammad Ucup. Absen Masuk berhasil dicatat.\"\n"
        "• Detik 3.5: Layar kembali ke mode Standby, siap melayani antrean karyawan berikutnya."
    )

    add_body_p("Skenario 2: Percobaan Titip Absen (Akses Ditolak)", bold_prefix="🔴 ")
    add_body_p(
        "Karyawan bernama Budi bangun kesiangan dan menitipkan kartunya ke temannya, Doni. Doni men-tap kartu milik Budi di sensor.\n"
        "Komputer mengenali nomor kartu Budi, tetapi saat kamera menyala, AI melihat wajah Doni. "
        "AI mencocokkan wajah Doni dengan arsip foto Budi, dan menghasilkan tingkat kecocokan hanya 25% (Wajah Berbeda!).\n"
        "Layar langsung menyala MERAH terang dengan tulisan: 'AKSES DITOLAK: Wajah Tidak Cocok dengan Pemilik Kartu!' "
        "dan komputer bersuara: 'Verifikasi wajah gagal!'. Kehadiran Budi tidak tercatat, dan kecurangan berhasil digagalkan."
    )

    # -------------------------------------------------------------
    # 6. RAHASIA DAPUR AI
    # -------------------------------------------------------------
    add_section_heading("6", "BAGAIMANA CARA AI MENGENALI WAJAH KITA? (RAHASIA DAPUR AI)")
    add_body_p(
        "Bagi orang awam, kemampuan komputer mengenali wajah terasa seperti sihir. Sebenarnya, bagaimana komputer bekerja?"
    )
    add_bullet_point("Tahap 1: Menemukan Posisi Wajah (Haar Cascade):", "Kamera melihat seluruh ruangan (tembok, baju, lampu). Komputer mencari pola khusus: 'Di mana ada dua mata, satu hidung, dan satu mulut?'. Begitu ketemu, komputer mengunci kotak hijau di wajah Anda.")
    add_bullet_point("Tahap 2: Menghilangkan Gangguan Cahaya (Grayscale & Equalization):", "Foto diubah menjadi hitam-putih. Bagian yang terlalu gelap diterangkan dan yang silau diredam agar warna lampu kantor tidak mengecoh komputer.")
    add_bullet_point("Tahap 3: Membaca Tekstur Unik (Algoritma LBPH):", "Komputer membagi wajah menjadi kotak-kotak kecil, lalu mengukur pola bayangan dahi, jarak mata, lekuk hidung, dan garis dagu. Semua ciri khas ini diubah menjadi kode angka matematika (histogram unik).")
    add_bullet_point("Tahap 4: Rahasia Multi-Burst 6 Foto:", "Jika kamera hanya menjepret 1 foto dalam 1 detik, bisa saja karyawan pas sedang berkedip atau menoleh. Sistem kami mengambil 6 foto berturut-turut dalam waktu 0.6 detik dan memilih foto terbaik. Itulah sebabnya verifikasi sangat akurat dan cepat!")

    # -------------------------------------------------------------
    # 7. FASILITAS HRD
    # -------------------------------------------------------------
    add_section_heading("7", "FASILITAS UNTUK BAGIAN HRD / MANAJEMEN (PORTAL ADMIN)")
    add_body_p(
        "Pimpinan perusahaan dan staf HRD memiliki halaman khusus di browser beralamat di: http://localhost:5000/admin. "
        "Fasilitas utama yang disediakan meliputi:"
    )
    add_bullet_point("1. Dashboard Kehadiran Real-Time:", "Melihat grafik berapa pegawai yang hadir hari ini, siapa yang terlambat (dan berapa menit terlambatnya), serta siapa yang ditolak.")
    add_bullet_point("2. Pendaftaran Karyawan Baru & Kartu RFID:", "Cukup mengisi Nama, NIK, Departemen, dan Nomor Kartu. Jika karyawan resign dan dihapus, kartu RFID-nya otomatis bebas kembali untuk dipakai orang baru.")
    add_bullet_point("3. Pendaftaran Wajah Kilat (Face Enrollment):", "Cukup klik tombol 'Biometrik' di samping nama karyawan, webcam akan menyala, klik tombol foto 3–5 kali, dan AI otomatis langsung pintar mengenali wajah karyawan baru tersebut!")
    add_bullet_point("4. Rekap Laporan Otomatis ke Microsoft Excel / CSV:", "HRD tidak perlu lagi menghitung manual di akhir bulan. Cukup pilih rentang tanggal, klik 'Export CSV', dan file kehadiran lengkap siap dibuka di Microsoft Excel.")
    add_bullet_point("5. Pengaturan Jam Kerja & Pergantian Kamera:", "Bisa mengatur jam kantor (misal: 08:00, toleransi 15 menit), serta memilih apakah ingin menggunakan webcam bawaan laptop atau webcam USB eksternal hanya dengan 1 kali klik.")

    # -------------------------------------------------------------
    # 8. PANDUAN KABEL FISIK
    # -------------------------------------------------------------
    add_section_heading("8", "PANDUAN RANGKAIAN KABEL FISIK (SEDERHANA & JELAS)")
    add_body_p(
        "Semua 7 kabel dari modul RFID (papan biru) disambungkan HANYA ke deretan pin bagian bawah ESP32 "
        "(sisi yang memiliki tulisan pin 3V3). Sisi atas ESP32 dibiarkan kosong:"
    )

    table_kabel = doc.add_table(rows=8, cols=4)
    table_kabel.alignment = WD_TABLE_ALIGNMENT.CENTER
    kabel_headers = ["No", "Pin Modul RFID", "Colok ke Pin ESP32", "Penjelasan Fungsi Kabel"]
    for i, h_text in enumerate(kabel_headers):
        cell = table_kabel.cell(0, i)
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_kabel = [
        ("1", "3.3V (VCC)", "Pin 3V3", "Kabel Listrik Daya 3.3 Volt (Wajib 3.3V, jangan colok ke 5V)."),
        ("2", "RST", "Pin D4", "Kabel Sinyal Reset Otomatis modul RFID."),
        ("3", "GND", "Pin GND", "Kabel Arus Negatif / Massa (Ground)."),
        ("4", "MISO", "Pin D19", "Kabel Jalur Data Masuk (RFID mengirim kode ke ESP32)."),
        ("5", "MOSI", "Pin D23", "Kabel Jalur Data Keluar (ESP32 memberi perintah ke RFID)."),
        ("6", "SCK", "Pin D18", "Kabel Detak Jam (Clock) pengatur irama komunikasi data."),
        ("7", "SDA (SS)", "Pin D5", "Kabel Saklar Pemilih Sinyal (Chip Select).")
    ]

    for row_idx, k_row in enumerate(data_kabel, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text_val in enumerate(k_row):
            cell = table_kabel.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(text_val)
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 9. PANDUAN MENJALANKAN SISTEM
    # -------------------------------------------------------------
    add_section_heading("9", "PANDUAN MENJALANKAN SISTEM LANGKAH DEMI LANGKAH")
    add_bullet_point("Langkah 1:", "Colokkan kabel USB ESP32 ke laptop/PC Anda. Colokkan juga webcam eksternal jika menggunakannya.")
    add_bullet_point("Langkah 2:", "Buka terminal/PowerShell di laptop Anda, masuk ke folder proyek, dan jalankan perintah:\n.\\venv\\Scripts\\python.exe app.py")
    add_bullet_point("Langkah 3:", "Tunggu beberapa detik sampai muncul tulisan: 'SMART ATTENDANCE SYSTEM RUNNING...'.")
    add_bullet_point("Langkah 4:", "Buka Google Chrome atau Edge:\n• Buka http://localhost:5000 untuk layar terminal absensi karyawan.\n• Buka http://localhost:5000/admin untuk portal HRD / manajemen.")
    add_bullet_point("Langkah 5:", "Selesai! Sekarang siap digunakan untuk absensi sehari-hari.")

    # -------------------------------------------------------------
    # 10. TANYA JAWAB (FAQ)
    # -------------------------------------------------------------
    add_section_heading("10", "TANYA JAWAB YANG SERING DITANYAKAN (FAQ)")
    add_body_p("Q: Apakah sistem ini membutuhkan koneksi internet?", bold_prefix="1. ")
    add_body_p("Jawab: Tidak perlu. Sistem AI dan databasenya berjalan 100% lokal (offline) di laptop Anda. Sangat aman dan foto karyawan tidak akan bocor ke internet.")

    add_body_p("Q: Bagaimana jika karyawan memakai kacamata atau mengubah gaya rambut?", bold_prefix="2. ")
    add_body_p("Jawab: AI LBPH mengenali struktur tulang dan tekstur bayangan wajah, bukan hanya rambut. Agar semakin akurat, saat mendaftar cukup ambil beberapa foto: 2 foto pakai kacamata dan 2 foto tanpa kacamata.")

    add_body_p("Q: Apakah kartu RFID bisa rusak jika sering ditempelkan?", bold_prefix="3. ")
    add_body_p("Jawab: Kartu RFID bekerja secara gelombang nirkabel tanpa gesekan fisik, sehingga chip di dalamnya sangat awet dan tahan bertahun-tahun.")

    # Save Document
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PANDUAN_SISTEM_ABSENSI_2FA.docx")
    doc.save(target_path)
    print(f"Document successfully created at: {target_path}")

if __name__ == "__main__":
    create_document()
