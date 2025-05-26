#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

const char* ssid = "李翊辰的iPhone";
const char* password = "11000000";

const char* serverUrl = "http://172.20.10.5:8080/sensor/upload/";

#define DHTPIN 27
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("已連上 WiFi");
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (!isnan(temp) && !isnan(hum)) {
    Serial.print("溫度: ");
    Serial.print(temp);
    Serial.print("°C, 濕度: ");
    Serial.print(hum);
    Serial.println("%");

    HTTPClient http;
    Serial.print("連接到: ");
    Serial.println(serverUrl);
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"temperature\": " + String(temp, 1) + 
                     ", \"humidity\": " + String(hum, 1) + "}";
    Serial.print("發送數據: ");
    Serial.println(payload);

    int httpResponseCode = http.POST(payload);
    Serial.println("回應碼: " + String(httpResponseCode));
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("伺服器回應: " + response);
    } else {
      Serial.print("連接失敗，錯誤碼: ");
      Serial.println(httpResponseCode);
      Serial.println("請確認伺服器 IP 與端口是否正確，以及伺服器是否運行中");
    }
    
    http.end();
  } else {
    Serial.println("感測器讀取失敗");
  }

  delay(10000);
}
