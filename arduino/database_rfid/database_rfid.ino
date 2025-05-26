#include "DHT.h"

#define DHTPIN 27
#define DHTTYPE DHT11
#define Led 2

String Str01 = "";
DHT dht1(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);    // 初始化 Serial 串口通訊
  dht1.begin();            // 初始化 DHT 感測器
  Serial.println("Ready"); // 回傳訊號給 Python 程式知道「準備完成」
  pinMode(Led, OUTPUT);    // 設定 LED 腳位為輸出
  digitalWrite(Led, LOW);  // 預設 LED 關閉
}
void loop() {
  if (Serial.available()) {
    Str01 = "";
    delay(10);

    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\n') break; // 遇到換行符號就停止
      Str01 += c;
    }

    Serial.println(Str01); // 印出收到的指令
  }

  // a 指令 → 開 LED 0.5 秒、關 0.5 秒
  if (Str01 == "a") {
    digitalWrite(Led, HIGH);
    delay(500);
    digitalWrite(Led, LOW);
    delay(500);
  }

  // b 指令 → 關 LED
  if (Str01 == "b") {
    digitalWrite(Led, LOW);
  }

  // c 指令 → 讀取 DHT11 濕度與溫度，並透過 Serial 傳出
  if (Str01 == "c") {
    float humidity = dht1.readHumidity();
    float temperature = dht1.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Failed to read from DHT sensor!");
    } else {
      Serial.print(humidity);
      Serial.print("% ");
      Serial.print(temperature);
      Serial.println("C");
    }
  }
}
