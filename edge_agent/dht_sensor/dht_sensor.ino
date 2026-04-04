/*
 * LabGuard DHT 센서 스케치
 *
 * DHT11 또는 DHT22 센서로 온습도를 읽어 LabGuard Edge Agent로 전송합니다.
 *
 * 필요한 것:
 *   - Arduino Uno
 *   - DHT11 또는 DHT22 센서
 *   - 10kΩ 저항 (DATA핀과 VCC 사이에 연결)
 *
 * 배선:
 *   DHT  핀1 (VCC)  → Arduino 5V
 *   DHT  핀2 (DATA) → Arduino D2  + 10kΩ 저항 → 5V
 *   DHT  핀4 (GND)  → Arduino GND
 *
 * 라이브러리 설치 (Arduino IDE):
 *   Sketch > Include Library > Manage Libraries
 *   → "DHT sensor library" by Adafruit 검색 후 설치
 *   → "Adafruit Unified Sensor" 도 함께 설치
 *
 * 센서 선택:
 *   DHT22 사용 시: SENSOR_TYPE = DHT22  (더 정확, 권장)
 *   DHT11 사용 시: SENSOR_TYPE = DHT11
 *
 * 출력 형식 (5초마다):
 *   {"T": 25.30, "H": 60.20}
 */

#include <DHT.h>

#define SENSOR_PIN  2       // DATA 핀 연결 위치
#define SENSOR_TYPE DHT11   // DHT22 또는 DHT11

DHT dht(SENSOR_PIN, SENSOR_TYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(2000);  // 센서 안정화 대기
}

void loop() {
  float humidity    = dht.readHumidity();
  float temperature = dht.readTemperature();

  // 읽기 실패 시 스킵
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("{\"error\": \"sensor read failed\"}");
    delay(5000);
    return;
  }

  // JSON 출력
  Serial.print("{\"T\":");
  Serial.print(temperature, 2);
  Serial.print(",\"H\":");
  Serial.print(humidity, 2);
  Serial.println("}");

  delay(5000);
}
