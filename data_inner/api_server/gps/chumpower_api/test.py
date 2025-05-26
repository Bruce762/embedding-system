import requests

# -------------------- API_G001_POST_TEST --------------------

# 傳送的參數
payload = {
    "Longitude": 125.5,
    "Latitude": 37.5
}

# POST 到 G001 API
r = requests.post("http://127.0.0.1:8000/G001/", json=payload)
# 顯示結果
print("上傳完成，伺服器回應：", r.text)

