"""
Author: Nguyen Khac Thanh
"""

import sys
import os
import signal
import logging
import logging.config
import pkg_resources


STOP_SIGNAL: int = 0
TEMP: str = os.path.join('/', 'tmp')
if sys.platform in ('linux', 'darwin'):
    TEMP = os.path.join('/', 'tmp')
elif sys.platform in ('win32',):
    TEMP = os.getenv('TEMP')
STOP_SIGNAL = signal.SIGTERM

PID = os.path.join(TEMP, 'leo.pid')

PRODUCT_API = '/api/products/'
ELS_UPDATE_PRODUCT_API = '/en/product/ajax_apiEditProductBatch'
ELS_GET_DEVICE_API = '/en/esl/ajax_api_getDeviceStatusBatch'

logging.config.fileConfig(
    pkg_resources.resource_filename('leo', 'logging_config.ini')
)

LEO_COMMAND = 'leo'
