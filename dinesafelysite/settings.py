"""
Django settings for dinesafelysite project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import django_heroku
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "4-wo^xhkbz@y1q7i*_yluq8p^pzl*k&7mm2df)b@v*e*@*6mwm"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "restaurant.apps.RestaurantConfig",
    "user.apps.UserConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dinesafelysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "dinesafelysite.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
                ".UserAttributeSimilarityValidator",
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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

YELP_BUSINESS_API = "https://api.yelp.com/v3/businesses/"
YELP_TOKEN_1 = (
    "JaekzvTTKsWGtQ96HUiwAXOUwRt6Ndbqzch4zc2XFnOEBxwTmwr"
    "-esm1uWo2QFvFJtXS8nY2dXx51cfAnMqVHpHRcp8N7QtP7LNVCcoxJWV_9NJrmZWSMiq"
    "-R_mEX3Yx "
)
YELP_ACCESS_TOKEN2 = (
    "A_V_V4rxelsvDsI2uFW1kT2mP2lUjd75GTEEsEcLnnvVOK5ssemrbw"
    "-R49czpANtS2ZtAeCl6FaapQrp1_30cRt9YKao3pFL1I6304sAtwKwKJk"
    "F1JBgF88FZl1_X3Yx "
)

YELP_ACCESS_TOKE = (
    "w5fGYpYDI6NYJOBI47KjmEJcROpCxq1VK841olTs0tSGOeGBNDuIIj8zF"
    "-C_MJFtAbrzfm7YF7bo72TxpOmrrn-zYnQ8xHBh_E4WEO39Z7IdKwbzCkBkCy0fjB6CX3Yx "
)

YELP_TOKEN_CHUANQI = (
    "xZS5Fvlspgk0IPac1_PTGHXShab3SErcTgweJcsDH77lXTDNbyaCFuH7c393oK41qXr0s_AnHb8fQ_"
    "PgsTUsFxhQqwuRqtCPiZu51OWevYAql7syUQuxc3AQC_-lX3Yx "
)

# Yelp categories
YELP_CATEGORY_API = "https://api.yelp.com/v3/categories/"
YELP_ACESS_TOKEN_BETA = (
    "Rp2eX_CuQVgaBc0Zk3sKRbFroy_s3_4eUtnNutojHg2G745uXH6-IakxKebxmc"
    "EcM2lIoOhGAjPcb_SoKx0evgi3YeRRre2Ago-9SWh_yGluXMwGAi03y9kIfEueX3Yx"
)

django_heroku.settings(locals(), test_runner=False)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {"format": "%(name)-12s %(levelname)-8s %(message)s"},
        "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": BASE_DIR / "logs/debug.log",
        },
    },
    "loggers": {"": {"level": "INFO", "handlers": ["console", "file"]}},
}

LOGOUT_REDIRECT_URL = "browse"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "dinesafely.nyc@gmail.com"
EMAIL_HOST_PASSWORD = "Nyucs2020"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
