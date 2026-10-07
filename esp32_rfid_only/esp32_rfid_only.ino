/*
 * =========================================================================
 * SMART ATTENDANCE 2FA - ESP32 RFID STANDALONE (TANPA LAYAR OLED)
 * =========================================================================
 * Board       : ESP32 Dev Module / NodeMCU-32S (30 Pin)
 * Komponen    : ESP32 + Modul RFID RC522 (HW-126)
 * Baud Rate   : 9600 baud (Kompatibel langsung dengan Flask app.py)
 * 
 * JALUR KABEL HANYA 7 KABEL (SPI):
 * -----------------------------------------------------------
 *   RC522 PIN   |  ESP32 PIN
 *   3.3V (VCC)  -->  3V3 (Pojok Kanan Bawah / Pin 3.3V)
 *   RST         -->  D4  (GPIO 4)
 *   GND         -->  GND
 *   IRQ         -->  (TIDAK DIGUNAKAN / KOSONG)
 *   MISO        -->  D19 (GPIO 19)
 *   MOSI        -->  D23 (GPIO 23)
 *   SCK         -->  D18 (GPIO 18)
 *   SDA (SS)    -->  D5  (GPIO 5)
 * =========================================================================
 */

#include <SPI.h>
#include <MFRC522.h>

// Konfigurasi Pin RFID SPI
#define SS_PIN    5   // D5
#define RST_PIN   4   // D4

// Indikator LED Bawaan ESP32 (Internal Blue LED)
#define LED_BUILTIN_PIN 2

MFRC522 rfrc522(SS_PIN, RST_PIN);

void setup() {
  // Inisialisasi Serial Komunikasi (9600 Baud)
  Serial.begin(9600);
  delay(500);

  // Inisialisasi LED internal ESP32
  pinMode(LED_BUILTIN_PIN, OUTPUT);
  digitalWrite(LED_BUILTIN_PIN, LOW);

  Serial.println("\n==========================================");
  Serial.println(" ESP32 RFID 2FA KIOSK - STANDALONE");
  Serial.println(" (Tanpa Layar OLED - Hanya RC522)");
  Serial.println("==========================================");

  // Inisialisasi SPI Bus & RC522
  SPI.begin();
  rfrc522.PCD_Init();
  delay(100);

  // Cek Status Modul RC522
  byte version = rfrc522.PCD_ReadRegister(rfrc522.VersionReg);
  if (version == 0x00 || version == 0xFF) {
    Serial.println("[WARN] Modul RFID RC522 BELUM TERDETEKSI!");
    Serial.println("  -> Pastikan tiap pin solderan RC522 tidak menyatu/korslet.");
    Serial.println("  -> Periksa kabel: 3V3, GND, D4, D5, D18, D19, D23.");
  } else {
    Serial.print("[OK] Modul RFID RC522 Siap! Firmware Versi: 0x");
    Serial.println(version, HEX);
    Serial.println(">> Tempelkan kartu / gantungan RFID ke reader...");

    // Kedipkan LED internal tanda siap
    digitalWrite(LED_BUILTIN_PIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN_PIN, LOW);
  }
}

void loop() {
  // 1. Cek apakah ada kartu RFID di dekat reader
  if (!rfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // 2. Baca serial UID kartu
  if (!rfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // 3. Konversi format byte UID ke string HEX uppercase (contoh: E2000019)
  String uidStr = "";
  for (byte i = 0; i < rfrc522.uid.size; i++) {
    if (rfrc522.uid.uidByte[i] < 0x10) uidStr += "0";
    uidStr += String(rfrc522.uid.uidByte[i], HEX);
  }
  uidStr.toUpperCase();

  // 4. Nyalakan LED internal ESP32 sebagai indikator tap berhasil
  digitalWrite(LED_BUILTIN_PIN, HIGH);

  // 5. Kirim UID kartu ke Serial Monitor & Flask app.py
  Serial.println(uidStr);

  // 6. Hentikan pembacaan kartu sementara (cegah spam tap berulang)
  rfrc522.PICC_HaltA();
  rfrc522.PCD_StopCrypto1();

  delay(250);
  digitalWrite(LED_BUILTIN_PIN, LOW);
  delay(1500); // Jeda 1.5 detik sebelum scan kartu berikutnya
}
