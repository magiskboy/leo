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
    STOP_SIGNAL = signal.SIGINT
    TEMP = os.path.join('/', 'tmp')
elif sys.platform in ('win32',):
    STOP_SIGNAL = signal.SIGQUIT
    TEMP = os.getenv('TEMP')

PID = os.path.join(TEMP, 'leo.pid')

PRODUCT_API = '/api/products/'
ELS_UPDATE_PRODUCT = '/en/product/ajax_apiEditProductBatch'

logging.config.fileConfig(
    pkg_resources.resource_filename('leo', 'logging_config.ini')
)

LEO_COMMAND = 'leo'
