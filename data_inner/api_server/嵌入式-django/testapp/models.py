from django.db import models

# Create your models here.

class TestModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DHT(models.Model):
    temperature = models.FloatField()         # 溫度（°C）
    humidity = models.FloatField()            # 濕度（%）
    recorded_at = models.DateTimeField(auto_now_add=True)  # 自動紀錄時間

    def __str__(self):
        return f"{self.recorded_at} | 溫度: {self.temperature}°C | 濕度: {self.humidity}%"
