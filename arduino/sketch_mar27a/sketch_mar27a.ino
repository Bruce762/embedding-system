#include "DHT.h"
#define DHTPIN 27 
#define DHTTYPE DHT11 
#include <SPI.h>
#include <MFRC522.h>
// **這一行是關鍵，宣告 dht1 變數**
DHT dht1(DHTPIN, DHTTYPE);	 
String read_id;
MFRC522 rfid(/*SS_PIN*/ 5, /*RST_PIN*/ 22);
void setup()
{
  Serial.begin(115200);
  dht1.begin(); 
  SPI.begin();
  rfid.PCD_Init();
  pinMode(26, INPUT);//光敏
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
    Serial.print("相對溼度,");
    Serial.print(dht1.readHumidity());
    Serial.print(",攝氏溫度,");
    Serial.print(dht1.readTemperature());
    Serial.print(",華氏溫度,");
    Serial.print(dht1.readTemperature(true));
    Serial.print(",RFID,");
    Serial.print(read_id);
    Serial.print(",光敏電阻,");
    Serial.println(analogRead(26));//光敏
  }
  delay(1000);
}
