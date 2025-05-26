import pymysql

try:
    # 先嘗試連接 MySQL 服務器
    db = pymysql.connect(
        host="127.0.0.1",
        user="testt",
        password="test"
    )
    cursor = db.cursor()
    
    # 列出所有資料庫
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    print("現有的資料庫：")
    for database in databases:
        print(database[0])
        
    # 檢查是否存在 chumpower_gps
    cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'chumpower_gps'")
    result = cursor.fetchone()
    
    if result:
        print("\nchumpower_gps 資料庫已存在")
    else:
        print("\nchumpower_gps 資料庫不存在")
        print("正在創建資料庫...")
        cursor.execute("CREATE DATABASE chumpower_gps")
        print("資料庫創建成功！")
    
except Exception as e:
    print(f"錯誤：{str(e)}")
finally:
    if 'db' in locals():
        db.close() 