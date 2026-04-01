/*
 * LabGuard Arduino 에뮬레이터
 *
 * 항온항습기(JEIO TECH 등)의 RS-232 동작을 흉내냅니다.
 * 실제 장비 없이 Edge Agent 통신 레이어를 테스트할 때 사용합니다.
 *
 * 출력 형식 (5초마다):
 *   {"T": 25.30, "H": 60.20}
 *
 * 이상값 주입 (10% 확률):
 *   온도 상한 초과: T = 42.0°C (임계치 max 35.0 초과)
 *   습도 상한 초과: H = 95.0%  (임계치 max 80.0 초과)
 *
 * 연결:
 *   Arduino Uno → USB → MacBook
 *   Tools > Port 에서 포트 선택 후 스케치 업로드
 *   baud rate: 9600
 */

// 정상 범위
const float TEMP_MIN  = 23.0;
const float TEMP_MAX  = 27.0;
const float HUMID_MIN = 55.0;
const float HUMID_MAX = 65.0;

// 이상값
const float TEMP_ANOMALY  = 42.0;
const float HUMID_ANOMALY = 95.0;

// 이상값 주입 확률 (0~99 중 몇 이하면 이상값)
const int ANOMALY_THRESHOLD = 10;  // 10%

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(A0));
}

float randFloat(float minVal, float maxVal) {
  return minVal + (float)random(0, 10000) / 10000.0 * (maxVal - minVal);
}

void loop() {
  float temp, humid;
  bool isAnomaly = (random(100) < ANOMALY_THRESHOLD);

  if (isAnomaly) {
    // 온도 또는 습도 중 하나를 이상값으로 주입
    if (random(2) == 0) {
      temp  = TEMP_ANOMALY + randFloat(-0.5, 0.5);
      humid = randFloat(HUMID_MIN, HUMID_MAX);
    } else {
      temp  = randFloat(TEMP_MIN, TEMP_MAX);
      humid = HUMID_ANOMALY + randFloat(-1.0, 1.0);
    }
  } else {
    temp  = randFloat(TEMP_MIN, TEMP_MAX);
    humid = randFloat(HUMID_MIN, HUMID_MAX);
  }

  // JSON 출력
  Serial.print("{\"T\":");
  Serial.print(temp, 2);
  Serial.print(",\"H\":");
  Serial.print(humid, 2);
  Serial.println("}");

  delay(5000);
}
