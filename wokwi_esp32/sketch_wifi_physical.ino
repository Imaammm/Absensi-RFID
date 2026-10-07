/*
 * =========================================================================
 * SMART ATTENDANCE 2FA - ESP32 FIRMWARE (PHYSICAL HARDWARE / ARDUINO IDE)
 * Full Edition with WiFi & HTTP POST
 * Upload ini menggunakan Arduino IDE saat menggunakan ESP32 Fisik Asli
 * =========================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define PIN_BUZZER    18
#define PIN_LED_GREEN 4
#define PIN_LED_RED   2

#define BTN_BUDI      13
#define BTN_SITI      12
#define BTN_DIMAS     14
#define BTN_UNKNOWN   27

// Sesuaikan nama Wi-Fi dan Password Rumah / Kantor Anda
const char* WIFI_SSID     = "NAMA_WIFI_ANDA";
const char* WIFI_PASSWORD = "PASSWORD_WIFI";

// Masukkan IP Laptop tempat Flask berjalan
const char* SERVER_URL    = "http://192.168.100.16:5000/api/rfid-tap";

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
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.fillRect(0, 0, SCREEN_WIDTH, 14, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(14, 3);
  display.print("SMART ATTENDANCE");
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 22);
  display.print("Status: WiFi Connected");
  display.setCursor(4, 36);
  display.print("Silakan Tap Kartu...");
  display.drawLine(0, 50, SCREEN_WIDTH, 50, SSD1306_WHITE);
  display.setCursor(4, 54);
  display.print("Ready to Scan");
  display.display();
}

void showScannedScreen(const char* uid, const char* name) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.fillRect(0, 0, SCREEN_WIDTH, 14, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(14, 3);
  display.print("KARTU TERDETEKSI");
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 20);
  display.print("UID : ");
  display.print(uid);
  display.setCursor(4, 33);
  display.print("Nama: ");
  display.print(name);
  display.setCursor(4, 48);
  display.print("-> Kirim ke Server...");
  display.display();
}

void sendRfidTap(const char* uid, const char* name) {
  showScannedScreen(uid, name);
  tone(PIN_BUZZER, 2200, 80);
  delay(100);
  tone(PIN_BUZZER, 2600, 100);

  Serial.println(uid);

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    String jsonBody = "{\"uid\":\"" + String(uid) + "\"}";
    int httpCode = http.POST(jsonBody);
    if (httpCode > 0) {
      Serial.println("[HTTP] Sent successfully: " + String(httpCode));
    }
    http.end();
    digitalWrite(PIN_LED_GREEN, LOW);
  }

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

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("[WARN] OLED tidak ditemukan");
  }

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(300);
    Serial.print(".");
    attempts++;
  }

  showStandbyScreen();
}

void loop() {
  if (digitalRead(BTN_BUDI) == LOW) {
    delay(40);
    if (digitalRead(BTN_BUDI) == LOW) sendRfidTap(CARDS[0].uid, CARDS[0].name);
  }
  if (digitalRead(BTN_SITI) == LOW) {
    delay(40);
    if (digitalRead(BTN_SITI) == LOW) sendRfidTap(CARDS[1].uid, CARDS[1].name);
  }
  if (digitalRead(BTN_DIMAS) == LOW) {
    delay(40);
    if (digitalRead(BTN_DIMAS) == LOW) sendRfidTap(CARDS[2].uid, CARDS[2].name);
  }
  if (digitalRead(BTN_UNKNOWN) == LOW) {
    delay(40);
    if (digitalRead(BTN_UNKNOWN) == LOW) sendRfidTap(CARDS[3].uid, CARDS[3].name);
  }
  delay(15);
}
