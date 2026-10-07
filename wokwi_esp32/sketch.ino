/*
 * =========================================================================
 * SMART ATTENDANCE 2FA - ESP32 WOKWI FAST-COMPILE EDITION
 * Super Cepat Dikompilasi di Wokwi (Tanpa Timeout / Server Busy)
 * =========================================================================
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// =========================================================================
// KONFIGURASI PIN
// =========================================================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Output
#define PIN_BUZZER    18
#define PIN_LED_GREEN 4
#define PIN_LED_RED   2

// Tombol Simulasi Kartu RFID (Input Pullup: aktif saat ditekan / LOW)
#define BTN_BUDI      13  // Kartu 1: Budi Santoso (E2000019)
#define BTN_SITI      12  // Kartu 2: Siti Rahma   (A134F90B)
#define BTN_DIMAS     14  // Kartu 3: Dimas Pratama (8833DC1A)
#define BTN_UNKNOWN   27  // Kartu 4: Kartu Asing   (UNKNOWN_99X)

// Data Kartu Dummy
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

// =========================================================================
// DISPLAY OLED HELPERS
// =========================================================================
void showStandbyScreen() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Header
  display.fillRect(0, 0, SCREEN_WIDTH, 14, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(14, 3);
  display.print("SMART ATTENDANCE");

  // Body
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 22);
  display.print("Status: STANDBY");

  display.setCursor(4, 36);
  display.print("Silakan Tap Kartu...");

  // Footer
  display.drawLine(0, 50, SCREEN_WIDTH, 50, SSD1306_WHITE);
  display.setCursor(4, 54);
  display.print("Tekan Tombol 1 - 4");

  display.display();
}

void showScannedScreen(const char* uid, const char* name, bool isKnown) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Header
  display.fillRect(0, 0, SCREEN_WIDTH, 14, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(14, 3);
  display.print("KARTU TERDETEKSI");

  // Detail
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 20);
  display.print("UID : ");
  display.print(uid);

  display.setCursor(4, 33);
  display.print("Nama: ");
  display.print(name);

  display.setCursor(4, 48);
  if (isKnown) {
    display.print("-> Scan Wajah 2FA...");
  } else {
    display.print("-> Akses Ditolak!");
  }

  display.display();
}

// =========================================================================
// FEEDBACK SUARA & LED
// =========================================================================
void triggerTapFeedback(bool isKnown) {
  if (isKnown) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    tone(PIN_BUZZER, 2200, 80);
    delay(100);
    tone(PIN_BUZZER, 2600, 100);
    delay(300);
    digitalWrite(PIN_LED_GREEN, LOW);
  } else {
    digitalWrite(PIN_LED_RED, HIGH);
    tone(PIN_BUZZER, 400, 200);
    delay(220);
    tone(PIN_BUZZER, 300, 300);
    delay(400);
    digitalWrite(PIN_LED_RED, LOW);
  }
}

// =========================================================================
// PROSES PENGIRIMAN DATA
// =========================================================================
void handleCardTap(int cardIndex) {
  const char* uid = CARDS[cardIndex].uid;
  const char* name = CARDS[cardIndex].name;
  bool isKnown = (cardIndex < 3);

  // Update Layar
  showScannedScreen(uid, name, isKnown);

  // Kirim Output Serial ke Terminal (Dibaca oleh Flask app.py jika dihubungkan)
  Serial.println(uid);
  Serial.print("[ESP32] RFID UID Sent: ");
  Serial.print(uid);
  Serial.print(" | ");
  Serial.println(name);

  // Bunyikan Buzzer & Nyalakan LED
  triggerTapFeedback(isKnown);

  delay(2000);
  showStandbyScreen();
}

// =========================================================================
// SETUP
// =========================================================================
void setup() {
  Serial.begin(9600);
  delay(200);

  Serial.println("\n=========================================");
  Serial.println(" SMART ATTENDANCE 2FA - ESP32 WOKWI");
  Serial.println("=========================================");

  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  pinMode(BTN_BUDI, INPUT_PULLUP);
  pinMode(BTN_SITI, INPUT_PULLUP);
  pinMode(BTN_DIMAS, INPUT_PULLUP);
  pinMode(BTN_UNKNOWN, INPUT_PULLUP);

  // Inisialisasi OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("[WARN] OLED SSD1306 tidak ditemukan pada 0x3C!");
  }

  // Nada Sambutan
  tone(PIN_BUZZER, 1800, 100);
  delay(120);
  tone(PIN_BUZZER, 2400, 120);

  showStandbyScreen();
}

// =========================================================================
// LOOP
// =========================================================================
void loop() {
  // Tombol 1: Budi
  if (digitalRead(BTN_BUDI) == LOW) {
    delay(40);
    if (digitalRead(BTN_BUDI) == LOW) {
      handleCardTap(0);
    }
  }

  // Tombol 2: Siti
  if (digitalRead(BTN_SITI) == LOW) {
    delay(40);
    if (digitalRead(BTN_SITI) == LOW) {
      handleCardTap(1);
    }
  }

  // Tombol 3: Dimas
  if (digitalRead(BTN_DIMAS) == LOW) {
    delay(40);
    if (digitalRead(BTN_DIMAS) == LOW) {
      handleCardTap(2);
    }
  }

  // Tombol 4: Asing
  if (digitalRead(BTN_UNKNOWN) == LOW) {
    delay(40);
    if (digitalRead(BTN_UNKNOWN) == LOW) {
      handleCardTap(3);
    }
  }

  delay(15);
}
