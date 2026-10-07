/*
 * =========================================================================
 * ESP32 - ZERO EXTERNAL LIBRARIES (TANPA ADAFRUIT / TANPA WIRE)
 * Khusus jika Wokwi ESP32 build server lambat
 * Cukup kosongi file libraries.txt di Wokwi
 * =========================================================================
 */

#define PIN_BUZZER    18
#define PIN_LED_GREEN 4
#define PIN_LED_RED   2

#define BTN_BUDI      13
#define BTN_SITI      12
#define BTN_DIMAS     14
#define BTN_UNKNOWN   27

const char* UIDS[] = {"E2000019", "A134F90B", "8833DC1A", "UNKNOWN_99X"};
const char* NAMES[] = {"Budi Santoso", "Siti Rahma", "Dimas Pratama", "Kartu Asing"};

void setup() {
  Serial.begin(9600);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  pinMode(BTN_BUDI, INPUT_PULLUP);
  pinMode(BTN_SITI, INPUT_PULLUP);
  pinMode(BTN_DIMAS, INPUT_PULLUP);
  pinMode(BTN_UNKNOWN, INPUT_PULLUP);

  Serial.println("ESP32 RFID Terminal Ready (Tekan tombol 1-4)");
}

void tap(int i) {
  Serial.println(UIDS[i]);
  Serial.print("[TAP] ");
  Serial.print(UIDS[i]);
  Serial.print(" - ");
  Serial.println(NAMES[i]);

  if (i < 3) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    tone(PIN_BUZZER, 2000, 100);
    delay(200);
    digitalWrite(PIN_LED_GREEN, LOW);
  } else {
    digitalWrite(PIN_LED_RED, HIGH);
    tone(PIN_BUZZER, 400, 300);
    delay(300);
    digitalWrite(PIN_LED_RED, LOW);
  }
}

void loop() {
  if (digitalRead(BTN_BUDI) == LOW) { delay(40); if (!digitalRead(BTN_BUDI)) { tap(0); delay(1500); } }
  if (digitalRead(BTN_SITI) == LOW) { delay(40); if (!digitalRead(BTN_SITI)) { tap(1); delay(1500); } }
  if (digitalRead(BTN_DIMAS) == LOW) { delay(40); if (!digitalRead(BTN_DIMAS)) { tap(2); delay(1500); } }
  if (digitalRead(BTN_UNKNOWN) == LOW) { delay(40); if (!digitalRead(BTN_UNKNOWN)) { tap(3); delay(1500); } }
}
