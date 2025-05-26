#!/bin/bash
source venv/bin/activate
echo "Django 虛擬環境已激活！"
echo "Django 版本: $(python -c 'import django; print(django.get_version())')"
echo "提示: 使用 'python manage.py runserver' 啟動開發服務器" 