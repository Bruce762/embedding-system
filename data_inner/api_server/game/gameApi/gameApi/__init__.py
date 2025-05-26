# 這段程式碼的目的是讓 Django 能夠使用 PyMySQL 作為 MySQL 資料庫的驅動程式
# 因為 Django 預設使用 MySQLdb 作為 MySQL 驅動程式，但 MySQLdb 不支援 Python 3
# 所以我們使用 PyMySQL 來替代 MySQLdb

import pymysql

# 這行程式碼會將 PyMySQL 註冊為 MySQLdb，讓 Django 可以正常使用 MySQL 資料庫
pymysql.install_as_MySQLdb()
