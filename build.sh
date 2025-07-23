#!/usr/bin/env bash
set -e   # يوقف السكربت عند أول خطأ

echo "1) تثبيت المتطلبات"
pip install -r requirements.txt

echo "2) تشغيل المايجريتس"
python manage.py migrate --noinput

echo "3) جمع الملفات الثابتة"
python manage.py collectstatic --noinput

echo "✅ انتهى build.sh بنجاح"
