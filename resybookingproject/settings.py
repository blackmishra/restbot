import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv, find_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = os.path.join(BASE_DIR, "resybookingproject", "templates")
# Load environment definition file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Load Auth0 application settings into memory
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")

SECRET_KEY = os.environ.get("SECRET_KEY")
BASE_URL = os.environ.get("BASE_URL")
RESY_HEADERS = os.environ.get("HEADERS")


DEBUG = True
# DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# set the celery broker url
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
LOGIN_URL = 'login'

# set the celery result backend
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER_URL")

CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

# set the celery timezone
CELERY_TIMEZONE = "UTC"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "resy",
    "users",
    "django_celery_beat",
    "celery",
    "corsheaders",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':[
        "rest_framework.permissions.AllowAny",
    ]
}

ROOT_URLCONF = "resybookingproject.urls"
CORS_ORIGIN_ALLOW_ALL = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "resybookingproject.wsgi.application"


# Database

DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://shashank:admin1234@localhost:5432/restaurantdb",
        conn_max_age=600,
    )
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
# STATIC_ROOT = "/home/sas/Desktop/projects/resybookingproject/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
if not DEBUG:  # Tell Django to copy statics to the `staticfiles` directory
    # in your application directory on Render.
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    # Turn on WhiteNoise storage backend that takes care of compressing static files
    # and creating unique names for each version so they can safely be cached forever.
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
