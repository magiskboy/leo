"""
Author: Nguyen Khac Thanh
"""
from typing import (
    IO,
    Dict,
    Tuple
)
import os
import sys
import time
import signal
import subprocess
import asyncio
import urllib
import aiohttp
import logging

from leo import (
    _config,
    _utils
)


def run(file: IO, delay: int, detach: bool, addrs: Tuple[str, str]) -> None:
    """Setup before run process
    """
    if os.path.exists(_config.PID):
        logging.info('Task is ready')
        sys.exit(14)
    mapping: Dict[str, str] = _utils.read_mapping(file)
    if detach:
        s_process = subprocess.Popen([_config.LEO_COMMAND, 'run', file.name,
                                      '--delay', str(delay),
                                      '--psrv', addrs[0],
                                      '--els', addrs[1]],
                                     stdout=subprocess.DEVNULL)
        logging.info(f'Task is running in background with pid {s_process.pid}')
    else:
        _utils.make_pid_file()
        start(mapping, delay, addrs)


def stop_bg_process() -> str:
    """Stop process
    """
    if os.path.exists(_config.PID):
        with open(_config.PID, 'r') as pidfile:
            pid = int(pidfile.readline())
            os.kill(pid, _config.STOP_SIGNAL)
            logging.info(f'Stop process {pid} complete')
        return f'Stop process {pid} successfully'
    else:
        return 'No such process'


def start(mapping: Dict[str, str], delay: int, addrs: Tuple[str, str]) -> None:
    """
    Alive function
    """
    signal.signal(_config.STOP_SIGNAL, _utils.stop_handler)
    loop = asyncio.get_event_loop()
    url_p_srv = urllib.parse.urljoin(addrs[0], _config.PRODUCT_API)
    url_els_srv = urllib.parse.urljoin(addrs[1], _config.ELS_UPDATE_PRODUCT)

    while True:
        tasks = []
        sess = aiohttp.ClientSession()
        for sub_skus in _utils.split(list(mapping.keys())):
            coro = _utils.update_coro(sess, url_p_srv, url_els_srv, sub_skus)
            tasks.append(loop.create_task(coro))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.run_until_complete(sess.close())

        logging.info('Update done')
        if delay < 0:
            break
        time.sleep(delay)
    _utils.stop_handler()
