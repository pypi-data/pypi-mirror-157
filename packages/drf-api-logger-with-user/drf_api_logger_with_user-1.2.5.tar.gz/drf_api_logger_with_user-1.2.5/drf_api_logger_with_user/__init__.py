import os
from drf_api_logger_with_user.events import Events

if os.environ.get('RUN_MAIN', None) != 'true':
    default_app_config = 'drf_api_logger_with_user.apps.LoggerConfig'

API_LOGGER_SIGNAL = Events()
