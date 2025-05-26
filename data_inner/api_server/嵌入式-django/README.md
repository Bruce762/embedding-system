# 嵌入式系統溫濕度監控平台

這是一個基於 Django 開發的嵌入式系統監控平台，主要用於收集和展示溫濕度感測器數據，並提供 RESTful API 接口供其他系統整合使用。

## 功能特點

### 1. 溫濕度數據管理
- 即時數據上傳和存儲
- 歷史數據查詢和展示
- 支援 ESP32 等硬體設備直接上傳數據
- 提供完整的 RESTful API 接口

### 2. 串口監控
- 支援串口設備的即時監控
- 自動數據採集和存儲
- 可配置串口參數
- 支援啟動/停止監控控制

### 3. 圖片管理
- 支援圖片上傳和存儲
- 提供圖片下載功能
- 支援圖片檔案管理

### 4. API 接口
提供以下 RESTful API 端點：

#### DHT 感測器數據 API
- `GET /api/dht/` - 獲取所有溫濕度數據
- `POST /api/dht/create/` - 創建新的溫濕度記錄
- `GET /api/dht/latest/` - 獲取最新的溫濕度數據
- `DELETE /api/dht/<record_id>/delete/` - 刪除指定的數據記錄

#### 串口監控 API
- `POST /serial/monitor/data/` - 上傳串口監控數據
- `POST /serial/monitor/control/` - 控制串口監控（啟動/停止）
- `GET /serial/monitor/status/` - 獲取串口監控狀態

## 技術架構

- 後端框架：Django 5.0.4
- 數據庫：MySQL
- API 框架：Django REST framework
- 串口通訊：PySerial
- 前端模板：Django Templates

## 環境要求

- Python 3.12 或以上
- MySQL 5.7 或以上
- pip（Python 包管理器）
- 虛擬環境工具（推薦使用 venv）

## 安裝指南

### 1. 安裝 Python 依賴
```bash
# 創建並激活虛擬環境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安裝所需套件
pip install django==5.0.4
pip install djangorestframework
pip install pymysql
pip install pyserial
```

### 2. 數據庫設置
```sql
# 在 MySQL 中執行
CREATE DATABASE djangodb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 配置專案
編輯 `myproject/settings.py` 中的數據庫設置：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangodb',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 4. 初始化數據庫
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 創建管理員帳號
```bash
python manage.py createsuperuser
```

## 運行專案

1. 啟動開發服務器：
```bash
python manage.py runserver 8080
```

2. 訪問以下地址：
- 管理後台：http://localhost:8080/admin/
- API 文檔：http://localhost:8080/api/
- 串口監控：http://localhost:8080/serial/monitor/status/

## API 使用示例

### 1. 上傳溫濕度數據
```bash
curl -X POST http://localhost:8080/api/dht/create/ \
     -H "Content-Type: application/json" \
     -d '{"temperature": 25.6, "humidity": 65.3}'
```

### 2. 獲取最新數據
```bash
curl http://localhost:8080/api/dht/latest/
```

### 3. 控制串口監控
```bash
# 啟動監控
curl -X POST http://localhost:8080/serial/monitor/control/ \
     -d "action=start"

# 停止監控
curl -X POST http://localhost:8080/serial/monitor/control/ \
     -d "action=stop"
```

## 目錄結構說明

```
myproject/          # 主專案目錄
├── settings.py     # 專案設置
├── urls.py        # 主 URL 配置
└── wsgi.py        # WSGI 配置

testapp/           # 應用程式目錄
├── models.py      # 數據模型定義
├── views.py       # 視圖函數
├── urls.py        # URL 路由配置
├── admin.py       # 管理介面配置
└── templates/     # HTML 模板
```

## 注意事項

1. 安全性考慮
   - 在生產環境中請修改 `SECRET_KEY`
   - 關閉 `DEBUG` 模式
   - 設置適當的 `ALLOWED_HOSTS`

2. 數據庫
   - 定期備份數據
   - 在生產環境使用強密碼
   - 考慮使用連接池優化性能

3. 串口通訊
   - 確保串口設備正確連接
   - 檢查串口權限設置
   - 注意數據傳輸速率設置

## 故障排除

1. 數據庫連接問題
   - 檢查 MySQL 服務是否運行
   - 確認數據庫憑證正確
   - 檢查防火牆設置

2. 串口通訊問題
   - 確認設備連接狀態
   - 檢查串口權限
   - 驗證波特率設置

3. API 訪問問題
   - 確認服務器運行狀態
   - 檢查網絡連接
   - 驗證請求格式正確

## 貢獻指南

1. Fork 本專案
2. 創建特性分支
3. 提交變更
4. 發起合併請求

## 授權協議

本專案採用 MIT 授權協議。詳見 LICENSE 文件。

## 聯繫方式

如有問題或建議，請提交 Issue 或聯繫專案維護者。 