from django.db import models

class sensor_data(models.Model):
    distance = models.FloatField()
    responseTime = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='sensor_images/%Y/%m/%d/', null=True, blank=True)

    class Meta:
        db_table = 'sensor_data'  # 對應到 MySQL 中的表名

    def __str__(self):
        return f"Distance: {self.distance}, Response Time: {self.responseTime}, Time: {self.timestamp}"
    #這是 __str__ 方法，定義當你「印出這個物件」時要顯示的內容。
    #在 Django 中，當你在後台（admin）、shell、或 debug 印出一筆資料時，會用這個方法回傳的字串來呈現。
