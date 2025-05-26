import requests
import json

# -------------------- API_G000_GET_TEST --------------------

# 輸入要 GET 的 API 路徑
get_rdata = requests.get('http://127.0.0.1:8000/G000/')

# 將 Response 的內容以文字形式輸出
print(get_rdata.text)