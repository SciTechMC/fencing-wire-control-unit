// Fencing ctrl v4 20260215
// Arduino Nano
#include <Arduino.h>
#include <FastLED.h>

// Config

#define BUZZER 7

// FASTLED CONFIGURATION-------------------------------------------------------------------------------
#define LED_PIN 6       // De digitale pin waarop de DATA pin van de ledstrip is aangesloten
#define BRIGHTNESS 50   // Helderheid (0-255)
#define LED_TYPE WS2812 // Type LED-chip
#define COLOR_ORDER GRB // Kleurvolgorde van je strip (kan ook RGB zijn, controleer de specificaties)
#define NUM_LEDS 3      // Het totale aantal leds op je strip
CRGB leds[NUM_LEDS];    // Definieer de LED array
// ----------------------------------------------------------------------------------------------------

struct Line {
  char letter;      // 'A' / 'B' / 'C'
  int analogPin;    // Assigned analog ouput pin
  int digitalPin;   // Assigned digital output pin
  int led;          // Pin for the designated led
  float correction; // Correction value
  float Vin;        // Assigned Vin
  int rawData;      // Raw data read out
  int digitalData;  // Digital data read
  float Vout;       // Calculated Vout
  float resistance; // Calculated resistance
};
Line lines[] = {
  {'A', A0, 2, 0, -14.5, 4.13, 0, 0, 0.0, 0.0},  // Line A
  {'B', A2, 3, 1, -17.6, 4, 0, 0, 0.0, 0.0},     // Line B
  {'C', A4, 4, 2, -14.0, 4.1, 0, 0, 0.0, 0.0}    // Line C
};
#define LINE_A 0
#define LINE_B 1
#define LINE_C 2

bool read_a = true;
bool read_b = true;
bool read_c = true;

int alert_sequences = 2;  // How many times to be alerted on short circuit
int raw_alert = 100;      // Raw level required for alarm
float R1 = 22;            // Base resistance
unsigned int loopCounter = 0;

int check_short_circuit() {
  int lines_shorted = 0;
  for (int i = 0; i < 3; i++) {
    if (lines[i].rawData >= raw_alert) {
      lines_shorted++;
    }
  }

  // If less than 2 lines, it's not a cross-line short circuit
  if (lines_shorted < 2) {
    return 0;
  }

  // Visual/Audible Alarm logic
  FastLED.clear();
  for (int j = 0; j < alert_sequences; j++) {
    for (int i = 0; i < 3; i++) {
      if (lines[i].rawData > raw_alert) {
        leds[lines[i].led] = CRGB::Red;
      }
    }
    FastLED.show();
    tone(BUZZER, 1000, 500);
    delay(500);
    FastLED.clear();
    FastLED.show();
    tone(BUZZER, 800, 500);
    delay(500);
  }
  return lines_shorted;
}

char buffer[80];

void print_python_data(int line, int shortStatus) {
  char vStr[7], rStr[7];
  dtostrf(lines[line].Vout, 4, 2, vStr);
  dtostrf(lines[line].resistance, 4, 2, rStr);

  sprintf(buffer, "data:%u;%c;%d;%d;%d;%d;%d;%d;%s;%s;%d",
    loopCounter,
    lines[line].letter,
    lines[LINE_A].digitalData,
    lines[LINE_B].digitalData,
    lines[LINE_C].digitalData,
    lines[LINE_A].rawData,
    lines[LINE_B].rawData,
    lines[LINE_C].rawData,
    vStr,
    rStr,
    shortStatus
  );
  Serial.println(buffer);
}

void print_data(int line){ // Prints the current read data from global variables
  String letter = String(lines[line].letter);
  Serial.println(" ");
  Serial.println(" ------- Line " + letter + " ------- ");
  Serial.print("Output A: "); Serial.println(lines[LINE_A].digitalData);
  Serial.print("Output B: "); Serial.println(lines[LINE_B].digitalData);
  Serial.print("Output C: "); Serial.println(lines[LINE_C].digitalData);

  Serial.println(" ");

  Serial.print("Raw A: "); Serial.println(lines[LINE_A].rawData);
  Serial.print("Raw B: "); Serial.println(lines[LINE_B].rawData);
  Serial.print("Raw C: "); Serial.println(lines[LINE_C].rawData);

  Serial.println(" ");

  Serial.println("Vout " + letter + ": " + String(lines[line].Vout) + " V");
  Serial.println("Resistance " + letter + ": " + String(lines[line].resistance) + " Ω");
  Serial.println("----------------------");
}

void read_data(int line){
  digitalWrite(lines[line].digitalPin, HIGH);
  delay(50);
  lines[LINE_A].digitalData = digitalRead(lines[LINE_A].digitalPin);
  lines[LINE_B].digitalData = digitalRead(lines[LINE_B].digitalPin);
  lines[LINE_C].digitalData = digitalRead(lines[LINE_C].digitalPin);

  lines[LINE_A].rawData = analogRead(lines[LINE_A].analogPin);
  lines[LINE_B].rawData = analogRead(lines[LINE_B].analogPin);
  lines[LINE_C].rawData = analogRead(lines[LINE_C].analogPin);
  digitalWrite(lines[line].digitalPin, LOW);
  delay(50);
}

void calculate_resistance(int line){
    float data = lines[line].rawData;
    float Vin = lines[line].Vin;
    float correction = lines[line].correction;

    float rawVoltageSum = data * Vin;
    lines[line].Vout = (rawVoltageSum) / 1023.0;
    float voltageRatio = Vin / lines[line].Vout - 1.0;
    lines[line].resistance = R1 * voltageRatio + correction;  // 2 correctie weerstand
}

void update_led(){ // Updates all LEDs based on the resistance value
  for (int i = 0; i < 3; i++){
    int led = lines[i].led;
    float resistance = lines[i].resistance;
    if (resistance < 3) {
      leds[led] = CRGB::Green;
    } else if (resistance >= 3 && resistance < 5) {
      leds[led].setRGB(204, 102, 0); // Orange
      }
      else {
      leds[led] = CRGB::Red;
    }
  }
  FastLED.show();
}

void setup() {
  pinMode(lines[LINE_A].digitalPin, OUTPUT);
  pinMode(lines[LINE_B].digitalPin, OUTPUT);
  pinMode(lines[LINE_C].digitalPin, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  Serial.begin(57600);
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);  //Initialiseer de FastLED bibliotheek
  FastLED.setBrightness(BRIGHTNESS);    
  
  // Init and test LEDS / BUZZER
  for (int i = 0; i < 3;i++){
    leds[i] = CRGB::Red;
    FastLED.show();
    delay(200);
    leds[i].setRGB(204, 102, 0); //values : R/G/B > Orange
    FastLED.show();
    delay(200);
    leds[i] = CRGB::Green;
    FastLED.show();
    delay(200);
  }
  tone(BUZZER, 1200, 500);
  delay(500);
  tone(BUZZER, 800, 500);
  delay(500);
}

void loop() {
  Serial.println(" ");
  Serial.print("*********** Loop: " + String(loopCounter) + " **********");
if (read_c) {
    read_data(LINE_C);
    calculate_resistance(LINE_C);
    int statusC = check_short_circuit();
    print_data(LINE_C);
    print_python_data(LINE_C, statusC);
  }
  if (read_b) {
    read_data(LINE_B);
    calculate_resistance(LINE_B);
    int statusB = check_short_circuit();
    print_data(LINE_B);
    print_python_data(LINE_B, statusB);
  }
  if (read_a) {
    read_data(LINE_A);
    calculate_resistance(LINE_A);
    int statusA = check_short_circuit();
    print_data(LINE_A);
    print_python_data(LINE_A, statusA);
  }
  
  update_led();
  loopCounter++;
}