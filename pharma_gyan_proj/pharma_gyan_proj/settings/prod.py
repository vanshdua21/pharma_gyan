from .base import *
DEBUG = True


# *********** DATABASES ***********

localhost = '127.0.0.1'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "pharma_gyan",
        "USER": "pharmagyan",
        "PASSWORD": "PharmaGyan@21",
        "HOST": localhost,
        "PORT": 3306
    }
}

ROOT_URLCONF = 'pharma_gyan_proj.urls'

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'level': 'DEBUG',
#             'formatter': 'verbose',
#         },
#
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/opt/logs/debug.log',
#             'formatter': 'simple',
#         },
#         'file1': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': '/opt/logs/debug.log',
#             'maxBytes': 15728640,  # 1024 * 1024 * 15B = 15MB
#             'backupCount': 10,
#             'formatter': 'verbose',
#         },
#
#         'console1': {
#                 'class': 'logging.StreamHandler',
#                 'level': 'DEBUG',
#                 'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'apps': {
#             'handlers': ['file1'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'app': {
#             'handlers': ['file1'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
#     'formatters': {
#         'verbose': {
#             'format': log_format_brief
#         },
#         'simple': {
#             'format': log_format
#         },
#     },
# }

BASE_PATH="http://43.204.94.180:80/"
LOGIN_PATH="/pharma_gyan/editor/adminLogin"
SECURE_LOGIN_PATH="/pharma_gyan/editor/secureLogin/"