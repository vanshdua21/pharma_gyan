from .base import *
root_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', '..'))
bank = os.environ.get("BANK")
DEBUG = True

# *********** DATABASES ***********

localhost = '127.0.0.1'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "pharma_gyan",
        "USER": "root",
        "PASSWORD": "root",
        "HOST": "localhost",
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
#         'console1': {
#             'class': 'logging.StreamHandler',
#             'level': 'DEBUG',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'apps': {
#             'handlers': ['console1'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'app': {
#             'handlers': ['console1'],
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

BASE_PATH="http://127.0.0.1:8000"