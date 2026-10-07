/*
 * =========================================================================
 * SMART ATTENDANCE 2FA - ARDUINO UNO WOKWI EDITION
 * 100% Instan di Wokwi (Tanpa Antrean / Server Busy)
 * Kompatibel Langsung dengan Flask app.py via Serial Port (9600 baud)
 * =========================================================================
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Inisialisasi LCD 16x2 I2C (Alamat default 0x27)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Output Pins
#define PIN_BUZZER    8
#define PIN_LED_GREEN 12
#define PIN_LED_RED   11

// Tombol Simulasi Kartu RFID (Input Pullup: aktif saat ditekan)
#define BTN_BUDI      2  // Kartu 1: Budi Santoso (E2000019)
#define BTN_SITI      3  // Kartu 2: Siti Rahma   (A134F90B)
#define BTN_DIMAS     4  // Kartu 3: Dimas Pratama (8833DC1A)
#define BTN_UNKNOWN   5  // Kartu 4: Kartu Asing   (UNKNOWN_99X)

// Data Kartu Karyawan
struct Card {
  const char* uid;
  const char* name;
};

const Card CARDS[] = {
  {"E2000019", "Budi Santoso"},
  {"A134F90B", "Siti Rahma"},
  {"8833DC1A", "Dimas Pratama"},
  {"UNKNOWN_99X", "Kartu Asing"}
};

void showStandbyScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SMART ATTENDANCE");
  lcd.setCursor(0, 1);
  lcd.print("TAP KARTU (1-4)");
}

void showCardScanned(const char* uid, const char* name, bool isKnown) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("UID: ");
  lcd.print(uid);
  lcd.setCursor(0, 1);
  if (isKnown) {
    lcd.print("-> SCAN WAJAH...");
  } else {
    lcd.print("-> AKSES DITOLAK");
  }
}

void triggerFeedback(bool isKnown) {
  if (isKnown) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    tone(PIN_BUZZER, 2000, 80);
    delay(100);
    tone(PIN_BUZZER, 2500, 120);
    delay(300);
    digitalWrite(PIN_LED_GREEN, LOW);
  } else {
    digitalWrite(PIN_LED_RED, HIGH);
    tone(PIN_BUZZER, 400, 200);
    delay(250);
    tone(PIN_BUZZER, 300, 300);
    delay(350);
    digitalWrite(PIN_LED_RED, LOW);
  }
}

void handleCardTap(int index) {
  const char* uid = CARDS[index].uid;
  const char* name = CARDS[index].name;
  bool isKnown = (index < 3);

  // 1. Tampilkan di LCD
  showCardScanned(uid, name, isKnown);

  // 2. Cetak ke Serial Monitor (Dibaca oleh Flask app.py via COM port)
  Serial.println(uid);

  // 3. Suara & Indikator LED
  triggerFeedback(isKnown);

  delay(2000);
  showStandbyScreen();
}

void setup() {
  Serial.begin(9600);

  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  pinMode(BTN_BUDI, INPUT_PULLUP);
  pinMode(BTN_SITI, INPUT_PULLUP);
  pinMode(BTN_DIMAS, INPUT_PULLUP);
  pinMode(BTN_UNKNOWN, INPUT_PULLUP);

  // Inisialisasi LCD
  lcd.init();
  lcd.backlight();

  // Nada pembuka
  tone(PIN_BUZZER, 1800, 80);
  delay(100);
  tone(PIN_BUZZER, 2200, 100);

  showStandbyScreen();
}

void loop() {
  if (digitalRead(BTN_BUDI) == LOW) {
    delay(40);
    if (digitalRead(BTN_BUDI) == LOW) handleCardTap(0);
  }
  if (digitalRead(BTN_SITI) == LOW) {
    delay(40);
    if (digitalRead(BTN_SITI) == LOW) handleCardTap(1);
  }
  if (digitalRead(BTN_DIMAS) == LOW) {
    delay(40);
    if (digitalRead(BTN_DIMAS) == LOW) handleCardTap(2);
  }
  if (digitalRead(BTN_UNKNOWN) == LOW) {
    delay(40);
    if (digitalRead(BTN_UNKNOWN) == LOW) handleCardTap(3);
  }
  delay(20);
}
