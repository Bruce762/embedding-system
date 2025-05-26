#include "DHT.h"
#define DHTPIN 4 
#define DHTTYPE DHT11 
#include <SPI.h>
#include <MFRC522.h>
#include <Ultrasonic.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "尖頭賴瑞";
const char* password = "00000001";
const char* serverUrl = "http://172.20.10.2:8000/upload/"; //?
 
String read_id;
MFRC522 rfid(/*SS_PIN*/ 5, /*RST_PIN*/ 22);
Ultrasonic ultrasonic_26_27(26, 27);
unsigned long elapsedTime = 0;
unsigned long startTime;
double dis;

int ledPin = 12;

void setup()
{
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
  pinMode(ledPin, OUTPUT);
  
  // 初始化隨機數生成器
  randomSeed(analogRead(0));

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("已連上 WiFi");
}

String mfrc522_readID()
{
  String ret;
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial())  
   //讀取並確認不是重複卡片
  {
    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
    for (byte i = 0; i < rfid.uid.size; i++) {
      ret += (rfid.uid.uidByte[i] < 0x10 ? "0" : "");
      ret += String(rfid.uid.uidByte[i], HEX);
    }//轉成16進制儲存
  }
  rfid.PICC_HaltA();
  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
  return ret;//回傳已完成轉存之id
}

void loop()
{
  read_id = mfrc522_readID(); //呼叫函式取得16進制id
  if (read_id != "") {
    // 生成2000-4000毫秒（2-4秒）的隨機延遲時間
    long randomDelay = random(2000, 4001);
    
    // 倒數提示
    digitalWrite(ledPin, HIGH);
    delay(300);
    digitalWrite(ledPin, LOW);
    delay(300);
    digitalWrite(ledPin, HIGH);
    delay(300);
    digitalWrite(ledPin, LOW);
    delay(300);
    digitalWrite(ledPin, HIGH);
    delay(300);
    digitalWrite(ledPin, LOW);
    
    // 隨機等待時間
    delay(randomDelay);
    
    digitalWrite(ledPin, HIGH); 
    startTime = millis();   
    while(ultrasonic_26_27.convert(ultrasonic_26_27.timing(), Ultrasonic::CM) > 5.0){
      
    }
    elapsedTime = millis() - startTime;   
    dis = ultrasonic_26_27.convert(ultrasonic_26_27.timing(), Ultrasonic::CM);
    Serial.print("超聲波距離,");
    Serial.print(dis); 
    Serial.print(",反應時間,");
    Serial.println(elapsedTime);
    digitalWrite(ledPin, LOW); 

    //傳送
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"distance\": " + String(dis, 1) + 
                     ", \"responseTime\": " + String(elapsedTime) + "}";

    int httpResponseCode = http.POST(payload);
    Serial.println("回應碼: " + String(httpResponseCode));
    http.end();
  }
}