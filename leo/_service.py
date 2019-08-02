"""
Author: Nguyen Khac Thanh
"""
from typing import (
    Tuple,
    Union
)
import os
import time
import signal
import subprocess
import asyncio
import logging
import aiohttp

from leo import (
    _config,
    _utils
)


def run(delay: int, detach: bool, addrs: Tuple[str, str]) -> Union[None, int]:
    """Setup before run process
    """
    os.remove(_config.PID)
    if detach:
        s_process = subprocess.Popen([_config.LEO_COMMAND, 'run',
                                      '--delay', str(delay),
                                      '--psrv', addrs[0],
                                      '--els', addrs[1]],
                                     stdout=subprocess.DEVNULL)
        logging.info('Task is starting in background')
    else:
        _utils.make_pid_file()
        start(delay, addrs)

    return s_process.pid or 0


def stop_bg_process() -> None:
    """Stop process
    """
    with open(_config.PID, 'r') as pidfile:
        pid = int(pidfile.readline())
        try:
            os.kill(pid, _config.STOP_SIGNAL)
        except OSError:
            pass


def start(delay: int, addrs: Tuple[str, str]) -> None:
    """
    Alive function
    """
    signal.signal(_config.STOP_SIGNAL, _utils.stop_handler)
    loop: asyncio.BaseEventLoop = asyncio.get_event_loop()

    while True:
        loop.run_until_complete(loop_iterator(addrs))
        logging.info('Update done')
        if delay < 0:
            break
        time.sleep(delay)
    _utils.stop_handler()


async def loop_iterator(addrs: Tuple[str, str]) -> None:
    """Iterator of update loop
    """
    coros = []
    sess = aiohttp.ClientSession()

    try:
        update_devices = await _utils.get_device_update(addrs[1], sess)
        skus = _utils.get_sku_from_device(update_devices)
    except aiohttp.ClientError as err:
        logging.error(err)
    else:
        for sub_skus in _utils.split(skus):
            coros.append(_utils.update_coro(sess, addrs, sub_skus))
        await asyncio.gather(*coros)
    finally:
        await sess.close()
