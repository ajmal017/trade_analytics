"""
Django settings for trade_analytics project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from . import db_routers
import datetime
from celery.schedules import crontab
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ku4tsp(r(o40s0=pfwlx@!eyvllqy^$p9@ur1azx=xa8&+p*ro'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.admindocs',
    'django_celery_results',
    'rest_framework',

    'home',
    'datascience',
    'charts',
    'stockapp',
    'dataapp',
    'computeapp',
    'django_rq',
]


# --------------------- WHICH TASK DISTRIBUTION YOU LIKE TO USE -------------##
# ---------------------------------------------------------------------------##
USE_REDIS = True
USE_CELERY = False

# --------------------- MIDDLEWARE -----------------------------------------##
# --------------------------------------------------------------------------##
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# --------------------- ROOT_URLCONF ---------------------------------------##
# --------------------------------------------------------------------------##

ROOT_URLCONF = 'trade_analytics.urls'


# --------------------- TEMPLATES -----------------------------------------##
# -------------------------------------------------------------------------##

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'trade_analytics.wsgi.application'


## --------------------- BIGDATA_DIR ---------------------------------------------------------------##
## ---------------------------------------------------------------------------------------------##

BIGDATA_DIR = os.path.join(BASE_DIR, 'bigdata')
if os.path.isdir(BIGDATA_DIR) == False:
    os.mkdir(BIGDATA_DIR)

## --------------------- DATABSE ---------------------------------------------------------------##
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
## ---------------------------------------------------------------------------------------------##


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'databases','db.sqlite3'),
#         'DESCRIPTION': "Primary and default router",
#     },
#     'initialization': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'databases', 'initialize.sqlite3'),
#         'DESCRIPTION': "This is an initial data base for initialization (to upload to github)",

#     },
#     'stockpricedata': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR,'databases', 'stockpricedata.sqlite3'),
#         'DESCRIPTION': "Save the large stock price data separately",

#     },
#     'featuredata': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR,'databases', 'featuredata.sqlite3'),
#         'DESCRIPTION': "Save Feature Data separately",

#     },
#     'datascience': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'databases' ,'datascience.sqlite3'),
#         'DESCRIPTION': "Independent Data sets for machine learning",
#     }
# }


# --------------------------POSTGRES --------------
IP = '192.168.2.103'
PORT = '5432'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'trade_analytics',
        'USER': os.getenv('DBUSER'),
        'PASSWORD': os.getenv('DBPASS'),
        'HOST': IP,
        'PORT': PORT,
        'DESCRIPTION': "Primary and default router",
    },
    'initialization': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'databases', 'initialize.sqlite3'),
        'DESCRIPTION': "This is an initial data base for initialization \
                                                (to upload to github)",

    },
    'stockpricedata': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'stockpricedata',
        'USER': os.getenv('DBUSER'),
        'PASSWORD': os.getenv('DBPASS'),
        'HOST': IP,
        'PORT': PORT,
        'DESCRIPTION': "Save the large stock price data separately",

    },
}


DATABASE_ROUTERS = ['trade_analytics.db_routers.StockPriceRouter',
                    'trade_analytics.db_routers.FeatureDataRouter',
                    'trade_analytics.db_routers.QueryDataRouter']
# dont forget to run
# python manage.py makemigrations
# python manage.py migrate
# python manage.py migrate  --database=stockpricedata
# python manage.py migrate  --database=featuredata
# python manage.py migrate  --database=querydata

## --------------------- PASSWORD ---------------------------------------------------------------##
# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators
## ---------------------------------------------------------------------------------------------##
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

## --------------------- INTERNATIONALIZATION ---------------------------------------------------------------##
# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
## ---------------------------------------------------------------------------------------------##
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Central'

USE_I18N = True

USE_L10N = True

USE_TZ = False

## --------------------- STATIC AND MEDIA ---------------------------------------------------------------##
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
## ---------------------------------------------------------------------------------------------##
STATIC_URL = '/static/'


## --------------------- LOGGING ---------------------------------------------------------------##
# Log to console and to file
## ---------------------------------------------------------------------------------------------##
if not os.path.isdir('logs'):
    os.mkdir('logs')

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '%(levelname)s, %(asctime)s, %(module)s, %(filename)s, %(funcName)s, %(lineno)d, %(process)d, %(thread)d, %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },


    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'debugfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'debug_' + datetime.datetime.today().strftime("%Y-%m-%d") + '.log'),
            'formatter': 'verbose',
        },

        'errorfile': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'error_' + datetime.datetime.today().strftime("%Y-%m-%d") + '.log'),
            'formatter': 'verbose',
        },

        'featureappfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'featureapp_' + datetime.datetime.today().strftime("%Y-%m-%d") + '.log'),
            'formatter': 'verbose',
        },

        'datasciencefile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'datascience_' + datetime.datetime.today().strftime("%Y-%m-%d") + '.log'),
            'formatter': 'verbose',
        },

        'dataappfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'dataapp_' + datetime.datetime.today().strftime("%Y-%m-%d") + '.log'),
            'formatter': 'verbose',
        },
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },

    },

    'loggers': {
        'django': {
            'handlers': ['console', 'debugfile', 'errorfile'],
            'propagate': True,
        },

        'debug': {
            'handlers': ['console', 'debugfile', 'errorfile'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'featureapp': {
            'handlers': ['console', 'featureappfile', 'errorfile'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'datascience': {
            'handlers': ['console', 'datasciencefile', 'errorfile'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'dataapp': {
            'handlers': ['console', 'dataappfile', 'errorfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        "rq.worker": {
            "handlers": ["rq_console"],
            "level": "DEBUG"
        },


    }

}

# --------------------------------------------------------------------#
# CELERY SETTINGS
# --------------------------------------------------------------------#

BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = 'US/Eastern'
CELERY_ENABLE_UTC = True,
CELERYD_MAX_TASKS_PER_CHILD = 20

CELERYBEAT_SCHEDULE = {}

# do the following
# celery -A trade_analytics worker -l info


# --------------------------------------------------------------------#
# REDIS SETTINGS
# --------------------------------------------------------------------#

RQ_QUEUES = {
    'default': {
        'HOST': '192.168.2.103',
        'PORT': 6379,
        'DB': 0,
        # 'PASSWORD': 'some-password',
        'DEFAULT_TIMEOUT': 360,
    },
    'ML': {
        'HOST': '192.168.2.103',
        'PORT': 6379,
        'DB': 0,
    }
}

# do the following
# redis-server trade_analytics/redis.conf
# python manage.py rqworker ML    .......for ML queue
# python manage.py rqworker       .......for default queue

# --------------------------------------------------------------------#
# JUPYTER NOTEBOOK SETTINGS
# --------------------------------------------------------------------#

# IPYTHON_ARGUMENTS = [
#     '--ext', 'django_extensions.management.notebook_extension',
# ]

NOTEBOOK_ARGUMENTS = [
    '--ip', '0.0.0.0',
    '--port', '1234',
    # '--ext', 'django_extensions.management.notebook_extension',
    # '--notebook-dir' , 'notebooks' ,
    '--debug',
]
SHELL_PLUS_PRE_IMPORTS = []

# --------------------------------------------------------------------#
# REST API SETTINGS
# --------------------------------------------------------------------#

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],

    'PAGE_SIZE': 10,

}
