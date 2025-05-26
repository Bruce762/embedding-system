from django.db import models

class dht(models.Model):
    temperature = models.FloatField()  # 溫度 (°C)
    humidity = models.FloatField()     # 濕度 (%)
    recorded_at = models.DateTimeField(auto_now_add=True)  # 自動紀錄時間

    def __str__(self):
        return f"{self.recorded_at}｜溫度: {self.temperature}°C｜濕度: {self.humidity}%"

class sensor_data(models.Model):  # ⚠️ 建議類別名稱改為駝峰式：SensorData
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'sensor_data'  # 對應的資料表名稱
        managed = False           # 表示這張表不是由 Django 自動建立（通常連接現有資料庫用）

    def __str__(self):
        return f"{self.timestamp}: {self.temperature}°C / {self.humidity}%"
