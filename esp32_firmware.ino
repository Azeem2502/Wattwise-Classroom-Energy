/*
 * ==============================================================================
 * Project: WattWise - Smart Classroom Energy Monitoring System
 * Target: ESP32-S3 Microcontroller
 * Sensors: ACS712-05B Current Sensor (via 10k/20k Divider) & PIR Motion Sensor
 * Communication: Wi-Fi HTTP POST (JSON Telemetry to Flask Server)
 * ==============================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // ArduinoJson v6 or v7

// ---------------- Wi-Fi Credentials ----------------
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ---------------- Backend Server Endpoint ----------------
const char* serverUrl = "http://192.168.1.100:5000/api/telemetry";

// ---------------- Pin Definitions ----------------
const int CURRENT_SENSOR_PIN = 4; // GPIO 4 (ADC1_CH3) connected to voltage divider output
const int PIR_SENSOR_PIN     = 5; // GPIO 5 connected to PIR Occupancy Sensor
const int RELAY_PIN          = 6; // GPIO 6 connected to Active-LOW Relay Module

// ---------------- Sensor Calibration Parameters ----------------
const float VREF_MV        = 3300.0; // ESP32 ADC Reference Voltage (3.3V)
const int   ADC_RESOLUTION = 4095;   // 12-bit ADC (0 - 4095)
const float DIVIDER_RATIO  = 1.50;   // Voltage divider ratio: (10k + 20k) / 20k = 30/20 = 1.5
const float ACS_OFFSET_MV  = 2500.0; // ACS712 Quiescent 0A Output (VCC / 2 = 2.5V)
const float ACS_SENSITIVITY= 185.0;  // 185 mV per Ampere for ACS712-05B module
const float SUPPLY_VOLTAGE = 5.0;    // Supply Voltage of load

// Previous current for derivative calculation (delta I)
float previousCurrent = 0.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[WattWise] Initializing ESP32-S3 Energy Monitor...");

  // Configure GPIOs
  pinMode(CURRENT_SENSOR_PIN, INPUT);
  pinMode(PIR_SENSOR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Relay OFF initially (Active LOW)

  // Configure ADC resolution & attenuation
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db); // Full range 0 - 3.3V

  // Connect to Wi-Fi
  Serial.printf("[Wi-Fi] Connecting to %s...", ssid);
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[Wi-Fi] Connected! IP Address: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[Wi-Fi] Failed to connect. Running in standalone sensor mode.");
  }
}

// Function to take multiple ADC samples for noise filtering
float readAveragedADC(int pin, int samples = 64) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delayMicroseconds(100);
  }
  return (float)sum / samples;
}

void loop() {
  // 1. Read ADC voltage at divider output
  float rawAdc = readAveragedADC(CURRENT_SENSOR_PIN, 64);
  float adcMillivolts = (rawAdc / ADC_RESOLUTION) * VREF_MV;

  // 2. Reconstruct original ACS712 Output Voltage (undo 1.5x divider attenuation)
  float acsOutMillivolts = adcMillivolts * DIVIDER_RATIO;

  // 3. Compute Current (I = (V_out - Offset) / Sensitivity)
  float currentAmps = (acsOutMillivolts - ACS_OFFSET_MV) / ACS_SENSITIVITY;
  if (currentAmps < 0.03) currentAmps = 0.0; // Low-current threshold clamp

  // 4. Calculate Rate of Change (Delta I)
  float deltaI = abs(currentAmps - previousCurrent);
  previousCurrent = currentAmps;

  // 5. Read Occupancy from PIR Sensor (1 = Occupied, 0 = Empty)
  int occupancy = digitalRead(PIR_SENSOR_PIN);

  // 6. Calculate Power (P = V * I)
  float powerWatts = SUPPLY_VOLTAGE * currentAmps;

  // Print telemetry to Serial Console
  Serial.println("----------------------------------------------");
  Serial.printf("ADC mV: %.1f | Sensor Out mV: %.1f\n", adcMillivolts, acsOutMillivolts);
  Serial.printf("Current: %.3f A | Power: %.2f W | Occ: %d | Delta I: %.3f\n", 
                currentAmps, powerWatts, occupancy, deltaI);

  // 7. Dispatch HTTP JSON POST to Flask Backend Server
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Construct JSON Payload
    StaticJsonDocument<256> doc;
    doc["device_id"]  = "ESP32_S3_ROOM_101";
    doc["voltage"]    = SUPPLY_VOLTAGE;
    doc["current"]    = round(currentAmps * 1000.0) / 1000.0;
    doc["power"]      = round(powerWatts * 100.0) / 100.0;
    doc["occupancy"]  = occupancy;
    doc["delta_i"]    = round(deltaI * 1000.0) / 1000.0;

    String jsonString;
    serializeJson(doc, jsonString);

    int httpCode = http.POST(jsonString);
    if (httpCode > 0) {
      String response = http.getString();
      Serial.printf("[Backend Response (%d)]: %s\n", httpCode, response.c_str());

      // Check if backend instructed a relay trip
      StaticJsonDocument<512> resDoc;
      deserializeJson(resDoc, response);
      if (resDoc["analysis"]["is_anomaly"].as<bool>() && occupancy == 0) {
        // Example: Trip relay if empty room energy waste persists
        // digitalWrite(RELAY_PIN, HIGH); // Disconnect load
      }
    } else {
      Serial.printf("[HTTP POST Error]: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }

  delay(1000); // 1 Hz sample rate
}
