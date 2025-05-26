from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pymysql, json, cv2
import numpy as np

# 圖片轉檔用
def convertToBinaryData(filename):
    pass  # TODO: 這裡的內容未補上

# 開始新增需要的功能：建立資料表
@csrf_exempt
def G000(request):
    # 判斷是否使用 GET 方法才處理
    if request.method == "GET":
        # 資料庫建立語法
        sql = (
            "CREATE TABLE GPS (ID Int AUTO_INCREMENT,"
            "Longitude FLOAT,"
            "Latitude FLOAT,"
            "Map BLOB,"
            "PRIMARY KEY (ID))"
        )

        try:
            # 資料庫連線
            db = pymysql.connect(
                host="127.0.0.1",
                user="testt",
                password="test",
                database="chumpower_gps"
            )

            # 使用 cursor() 方法建立一個游標對象 cursor
            cursor = db.cursor()

            # 使用 execute() 方法執行 SQL，如果資料表存在則刪除
            cursor.execute("DROP TABLE IF EXISTS GPS")

            # 執行建立資料表語法
            cursor.execute(sql)

            # 提交變更
            db.commit()
            print("創建完成")
            status = "OK"

        except:
            # 資料庫回傳錯誤訊息
            db.rollback()
            print("創建失敗")
            status = "ERROR"

        # 關閉資料庫連線
        db.close()

        # 回傳狀態
        return HttpResponse(status)
