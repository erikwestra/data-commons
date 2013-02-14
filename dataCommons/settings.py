""" dataCommons.settings

    This module defines the various settings for the dataCommons project.

    Note that to support deployment to Heroku, we use the SettingsImporter
    class to import settings from either an environment variable or a
    custom_settings.py module if it exists.
"""
import os
import os.path
import sys

import dj_database_url

from dataCommons.shared.lib.settingsImporter import SettingsImporter

#############################################################################

# Calculate the absolute path to the top-level directory for our server.

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#############################################################################

# Load our various custom settings.

import_setting = SettingsImporter(globals(),
                                  custom_settings="dataCommons.custom_settings",
                                  env_prefix="DC_")

import_setting("DEBUG",                     True)
import_setting("TIME_ZONE",                 "UTC")
import_setting("SERVE_STATIC_MEDIA",        False)
import_setting("DATABASE_URL",              None)
# NOTE: DATABASE_URL uses the following general format:
#           postgres://username:password@host:port/database_name
#       or for a database on the local machine:
#           postgres://username:password@localhost/database_name
import_setting("LOG_DIR",                   os.path.join(ROOT_DIR, "logs"))
import_setting("ENABLE_DEBUG_LOGGING",      False)
import_setting("ENABLE_QUERY_LOGGING",      False)
import_setting("LOGGING_DESTINATION",       "file")
import_setting("AWS_ACCESS_KEY_ID",         None)
import_setting("AWS_SECRET_ACCESS_KEY",     None)
import_setting("AWS_STORAGE_BUCKET_NAME",   None)
import_setting("AWS_S3_SECURE_URLS",        None)

import_setting("REDIS_HOST",                '10.5.5.1')
import_setting("REDIS_PORT",                6379)
import_setting("REDIS_PASSWORD",            None)

import_setting("QUERY_TIMEOUT",             20000)
import_setting("GEOS_LIBRARY_PATH",         None)
import_setting("GDAL_LIBRARY_PATH",         None)

import_setting("CELERY_ALWAYS_EAGER",       False)
import_setting("DJCELERY_BROKER_BACKEND",   None)
import_setting("DJCELERY_BROKER_URL",       None)
import_setting("DJCELERY_BROKER_OPTIONS",   None)
import_setting("DJCELERY_RESULT_BACKEND",   None)

#############################################################################

# Our various project settings:

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ''

MEDIA_URL = ''

APPEND_SLASH = True #False

STATIC_ROOT = ''

#STATIC_URL = '/static/'

STATICFILES_DIRS = (
    ("shared", os.path.join(ROOT_DIR, "dataCommons", "shared_static")),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

STATIC_URL = 'http://datacommons.3taps.com.s3.amazonaws.com/'

SECRET_KEY = 'be)s*7-3zpstvvb=jcbeiaqhnf4ks9#jf%uxn#v9_=w3=e^s9)'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Enable the django-cors middleware.

    'cors.middleware.AllowOriginMiddleware',
)

ROOT_URLCONF = 'dataCommons.urls'

WSGI_APPLICATION = 'dataCommons.wsgi.application'

TEMPLATE_DIRS = (
    os.path.dirname(__file__),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Enable the GIS extension.

    'django.contrib.gis',

    # Enable django-cors.

    'cors',

    # Enable the "south" database migration toolkit.

    'south',

    # Enable the "celery" task queuing system.

    'kombu.transport.django',
    'djcelery',

    # Install the Amazon S3 storage application.

    "storages",

    # Install our various data commons apps.

    "dataCommons.shared",
    "dataCommons.geolocator",
    "dataCommons.postingAPI",
    "dataCommons.searchAPI",
    "dataCommons.summarizerAPI",
    "dataCommons.monitoringAPI",
    "dataCommons.reporting",
    "dataCommons.admin",
)

# Enable djcelery.  Note that we use our own custom setting names (prefixed
# with "DJCELERY_") to avoid name clashes with Celery configuration variables.

if DJCELERY_BROKER_BACKEND != None:
    BROKER_BACKEND = DJCELERY_BROKER_BACKEND

if DJCELERY_BROKER_URL != None:
    BROKER_URL = DJCELERY_BROKER_URL

if DJCELERY_BROKER_OPTIONS != None:
    BROKER_TRANSPORT_OPTIONS = DJCELERY_BROKER_OPTIONS

if DJCELERY_RESULT_BACKEND != None:
    CELERY_RESULT_BACKEND = DJCELERY_RESULT_BACKEND

import djcelery
djcelery.setup_loader()

# Create our "log" directory if we've been asked to log debug messages or
# database queries.

if ((ENABLE_DEBUG_LOGGING or
     ENABLE_QUERY_LOGGING) and LOGGING_DESTINATION == "file"):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

# Start with our default logging configuration.

LOGGING = {
    'version'                  : 1,
    'disable_existing_loggers' : True,
    'handlers'                 : {},
    'loggers'                  : {},
    'formatters'               : {}
}

# Add our custom formatters.

LOGGING['formatters']['plain'] = \
    {'format' : "%(message)s"}

LOGGING['formatters']['timestamped'] = \
    {'format'  : "%(asctime)s %(message)s",
     'datefmt' : "%Y-%m-%d %H:%M:%S"}

# Configure logging if it is enabled.

if ENABLE_DEBUG_LOGGING or ENABLE_QUERY_LOGGING:

    log_handlers = []

    if ENABLE_DEBUG_LOGGING:
        if LOGGING_DESTINATION == "file":
            LOGGING['handlers']['debugger_log'] = \
                {'level'     : "DEBUG",
                 'class'     : "logging.FileHandler",
                 'filename'  : os.path.join(LOG_DIR, "debug.log"),
                 'formatter' : "timestamped"}
            log_handlers.append("debugger_log")
        elif LOGGING_DESTINATION == "console":
            LOGGING['handlers']['debugger_log'] = \
                {'level'     : "DEBUG",
                 'class'     : "logging.StreamHandler",
                 'formatter' : "plain"}
            log_handlers.append("debugger_log")
        else:
            raise RuntimeError("Unknown logging destination: " +
                               LOGGING_DESTINATION)

    if ENABLE_QUERY_LOGGING:
        if LOGGING_DESTINATION == "file":
            LOGGING['handlers']['query_log'] = \
                {'level'     : "DEBUG",
                 'class'     : "logging.FileHandler",
                 'filename'  : os.path.join(LOG_DIR, "query.log"),
                 'formatter' : "timestamped"}
            log_handlers.append("query_log")
        elif LOGGING_DESTINATION == "console":
            LOGGING['handlers']['query_log'] = \
                {'level'     : "DEBUG",
                 'class'     : "logging.StreamHandler",
                 'formatter' : "plain"}
            log_handlers.append("query_log")
        else:
            raise RuntimeError("Unknown logging destination: " +
                               LOGGING_DESTINATION)

    LOGGING['loggers']['dataCommons'] = {'handlers'  : log_handlers,
                                         'level'     : "DEBUG",
                                         'propogate' : False}

# Set up our database.

if 'test' in sys.argv:
    # Use SQLite for unit tests.
    DATABASES = {'default' : {'ENGINE' : "django.db.backends.sqlite3"}}
else:
    # Use dj_database_url to extract the database settings from the
    # DATABASE_URL setting.
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Set up our Redis instance.

REDIS_CONFIG = {}
if REDIS_HOST     != None: REDIS_CONFIG['host']     = REDIS_HOST
if REDIS_PORT     != None: REDIS_CONFIG['port']     = REDIS_PORT
if REDIS_PASSWORD != None: REDIS_CONFIG['password'] = REDIS_PASSWORD

