#!/usr/bin/env bash
set -e   # يوقف السكربت عند أول خطأ

echo "1) تثبيت المتطلبات"
pip install -r requirements.txt

echo "2) تشغيل المايجريتس"
python manage.py migrate --noinput

echo "3) جمع الملفات الثابتة"
python manage.py collectstatic --noinput


# 4. Create a superuser if one doesn't exist
python manage.py create_superuser
echo "✅ انتهى build.sh بنجاح"
