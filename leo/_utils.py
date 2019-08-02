"""
Author: Nguyen Khac Thanh
"""
from typing import (
    Dict,
    Tuple,
    Any,
    List,
    Coroutine,
    Iterable
)
import os
import sys
import urllib
import logging
import aiohttp

from leo import _config


def is_task_already():
    """Check task is running follow PID path
    """
    return os.path.exists(_config.PID)


def make_pid_file() -> None:
    """Helper functon for make pid file
    """
    with open(_config.PID, 'w') as pidfile:
        pid: str = os.getpid()
        pidfile.write(str(pid))


def stop_handler(sig: int = None, frame=None) -> None:
    """Callback function when trigger signal
    """
    os.remove(_config.PID)
    sys.exit(0)


def split(items: List[str], chuck_size: int = 10) -> Iterable:
    """Split list into chucks
    """
    items = list(items)
    while items:
        if len(items) < chuck_size:
            r_value = items
        else:
            r_value = items[:chuck_size]
        items = items[chuck_size:]
        yield r_value


async def get_device_update(els_srv: str, sess: aiohttp.ClientSession) -> Iterable:
    """Get all device expect update
    """
    def device_filter(device):
        return device['IS_ACTIVE'] & bool(device['Inventory Barcode'] is not None)

    url = urllib.parse.urljoin(els_srv, _config.ELS_GET_DEVICE_API)
    payload = {'device_type': 'ED'}
    res = await sess.post(url, json=payload)
    data = await res.json()
    all_devices = data['DEVICE']

    return filter(device_filter, all_devices)


def get_sku_from_device(devices: Dict[str, Any]) -> Iterable:
    """Extract only barcode[sku] from list of device
    """
    return map(lambda device: device['Inventory Barcode'], devices)


async def update_coro(sess: aiohttp.ClientSession,
                      addrs: Tuple[str, str],
                      skus: List[str]) -> Coroutine:
    """Update tags
    """
    try:
        pull_data_url = urllib.parse.urljoin(addrs[0], _config.PRODUCT_API)
        push_data_url = urllib.parse.urljoin(addrs[1], _config.ELS_UPDATE_PRODUCT_API)
        p_res = await sess.get(
            pull_data_url,
            params=_make_pull_product_request(skus)
        )
        data = await p_res.json()
        if p_res.status != 200:
            raise aiohttp.ClientPayloadError(f"Call product server: {data['message']}")
        els_res = await sess.post(
            push_data_url,
            json=_make_push_product_request(data['result']['products'], skus)
        )
        data = await els_res.json()
        if els_res.status != 200:
            raise aiohttp.ClientError(f"Call els server: {data['ERROR']}")
    except aiohttp.ClientError as err:
        logging.error(str(err))
    else:
        logging.info('Push data success')
        logging.info(data)


def _make_pull_product_request(skus: List[str], channel: str = 'pv_showroom',
                               terminal: int = 1) -> Dict[str, Any]:
    return {
        'channel': channel,
        'terminal': terminal,
        'skus': ','.join(skus)
    }


def _make_others_field(*args):
    args = map(lambda x: "" if x is None else str(x), args)
    return ','.join(args)


def _make_push_product_request(product_update: List[dict],
                               skus: List[str]) -> Dict[str, Any]:
    items = []
    for product in product_update:
        if product['sku'] in skus:
            item = {
                'No': product['sku'],
                'Barcode': str(product['sku']),
                'Layout Index': str(0),
                'Name': product['name'].split('/')[-1],
                'Area': 'None',
                'Other Fields': _make_others_field(
                    product['price']['sellPrice'],
                    product['price']['supplierSalePrice'],
                    product['seoInfo']['shortDescription']
                ),
                'action': 'M'
            }
            items.append(item)
    data = {
        'Inventory': items
    }

    return data
