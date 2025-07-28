# config/settings.py

from pathlib import Path
import os
import datetime
from dotenv import load_dotenv
import dj_database_url

# ──────────────────────────────────────────────────────────────────────────────
# المسار الأساسي وتحميل متغيرات البيئة (.env)
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ──────────────────────────────────────────────────────────────────────────────
# المفاتيح وأوضاع التشغيل
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# أثناء التطوير، أضف localhost و127.0.0.1 تلقائيًا
if DEBUG:
    ALLOWED_HOSTS += ['127.0.0.1', 'localhost']

# ──────────────────────────────────────────────────────────────────────────────
# إعداد قاعدة البيانات عبر Supabase Postgres URL
# ──────────────────────────────────────────────────────────────────────────────
# تأكد من أن DATABASE_URL في .env يبدأ بـ postgres:// أو postgresql://
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# ──────────────────────────────────────────────────────────────────────────────
# تطبيقات Django
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'journal',
    'companion',
    'goals',
    'info',
    'community',

    'simple_history',
    'rest_framework',
    'admin_interface',
    'colorfield',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ──────────────────────────────────────────────────────────────────────────────
# إعدادات القوالب
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# نموذج المستخدم المخصص
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'users.CustomUser'

# ──────────────────────────────────────────────────────────────────────────────
# التحقق من كلمات المرور
# ──────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────────────────────────────────────
# إعدادات i18n / l10n
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────────
# الملفات الثابتة (Static) و WhiteNoise
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────────────────────────────────────────
# الملفات المرفوعة (Media)
# ──────────────────────────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────────────────────────────────────
# التخزين السحابي عبر S3 (Supabase S3 أو AWS S3)
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID       = os.getenv('SUPABASE_S3_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('SUPABASE_S3_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('SUPABASE_S3_BUCKET_NAME')
AWS_S3_ENDPOINT_URL     = os.getenv('SUPABASE_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME      = os.getenv('SUPABASE_S3_REGION_NAME')

# ──────────────────────────────────────────────────────────────────────────────
# مفاتيح Supabase العامة والخاصة
# ──────────────────────────────────────────────────────────────────────────────
SUPABASE_URL              = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY         = os.getenv('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

# ──────────────────────────────────────────────────────────────────────────────
# إعداد البريد الإلكتروني
# ──────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND      = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
CONTACT_EMAIL      = os.getenv('CONTACT_EMAIL', 'admin@yourdomain.com')

# ──────────────────────────────────────────────────────────────────────────────
# Auth & Axes (حماية ضد هجمات brute force)
# ──────────────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_ENABLED       = os.getenv('AXES_ENABLED', 'True').lower() == 'true'
AXES_FAILURE_LIMIT = int(os.getenv('AXES_FAILURE_LIMIT', 5))
AXES_COOLOFF_TIME  = datetime.timedelta(minutes=int(os.getenv('AXES_COOLOFF_MINUTES', 30)))

# ──────────────────────────────────────────────────────────────────────────────
# تسجيل الدخول / الخروج
# ──────────────────────────────────────────────────────────────────────────────
# بعد DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# مسار صفحة تسجيل الدخول (يستخدم اسم الـ URL من users/urls.py)
LOGIN_URL = 'users:login'

# بعد تسجيل الدخول يعيد توجيه المستخدم إلى داشبورد journal
LOGIN_REDIRECT_URL = 'journal:dashboard'

# بعد تسجيل الخروج يعيد توجيه المستخدم إلى صفحة الهبوط info
LOGOUT_REDIRECT_URL = 'info:landing'
