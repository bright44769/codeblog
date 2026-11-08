import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '').strip()
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY when DEBUG is disabled.')
    SECRET_KEY = 'django-insecure-change-this-before-deployment'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
if not DEBUG and not os.environ.get('DJANGO_ALLOWED_HOSTS', '').strip():
    raise ImproperlyConfigured('Set DJANGO_ALLOWED_HOSTS to your production hostname.')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','django.contrib.sites','home.apps.HomeConfig','blog.apps.BlogConfig','allauth','allauth.account','allauth.socialaccount','allauth.socialaccount.providers.google','storages']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','home.middleware.RequireEmailMFA','allauth.account.middleware.AccountMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='codeblog.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='codeblog.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG,
    )
elif not DEBUG:
    raise ImproperlyConfigured('Set DATABASE_URL to the production PostgreSQL connection URL.')
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'; TIME_ZONE='Africa/Accra'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATICFILES_DIRS=[BASE_DIR/'static']; STATIC_ROOT=BASE_DIR/'staticfiles'
STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '').strip()
if AWS_STORAGE_BUCKET_NAME:
    if not DEBUG and not (os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')):
        raise ImproperlyConfigured('Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY for production media storage.')
    STORAGES['default'] = {'BACKEND': 'storages.backends.s3.S3Storage'}
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', '').strip() or None
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', '').strip() or None
    AWS_S3_FILE_OVERWRITE = False
elif not DEBUG:
    pass
MEDIA_URL='/media/'; MEDIA_ROOT=Path(os.environ.get('MEDIA_ROOT', BASE_DIR / 'media'))
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
SECURE_SSL_REDIRECT=not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS='DENY'
if not DEBUG:
    SECURE_HSTS_SECONDS=31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
SITE_ID=1
AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend','allauth.account.auth_backends.AuthenticationBackend']
LOGIN_REDIRECT_URL='/'; LOGOUT_REDIRECT_URL='/'; ACCOUNT_LOGIN_METHODS={'username','email'}; ACCOUNT_SIGNUP_FIELDS=['username*','email*','password1*','password2*']; ACCOUNT_EMAIL_VERIFICATION='none'
SOCIALACCOUNT_PROVIDERS={'google':{'APP':{'client_id':os.environ.get('GOOGLE_CLIENT_ID',''),'secret':os.environ.get('GOOGLE_CLIENT_SECRET',''),'key':''},'SCOPE':['profile','email'],'AUTH_PARAMS':{'access_type':'online'}}}
EMAIL_BACKEND=os.environ.get('EMAIL_BACKEND','django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST=os.environ.get('EMAIL_HOST','smtp.gmail.com')
EMAIL_PORT=int(os.environ.get('EMAIL_PORT','587'))
EMAIL_USE_TLS=os.environ.get('EMAIL_USE_TLS','True').lower() == 'true'
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER','').strip()
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD','').strip()
DEFAULT_FROM_EMAIL=os.environ.get('DEFAULT_FROM_EMAIL','').strip()
PUBLIC_SITE_URL=os.environ.get('PUBLIC_SITE_URL','').strip().rstrip('/')

placeholder_email_values={'your-email@gmail.com','yourrealgmail@gmail.com','example@gmail.com'}
placeholder_password_values={'your-16-character-app-password','16char_app_password','your_app_password','replace-me','your-16-char-app-password'}

if (not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD or EMAIL_HOST_USER.lower() in placeholder_email_values or EMAIL_HOST_PASSWORD.lower() in placeholder_password_values):
  
    EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST='localhost'
    EMAIL_PORT=1025
    EMAIL_USE_TLS=False
    DEFAULT_FROM_EMAIL='noreply@codeblog.local'
MESSAGE_TAGS={messages.DEBUG:'info',messages.INFO:'info',messages.SUCCESS:'success',messages.WARNING:'warning',messages.ERROR:'danger'}
