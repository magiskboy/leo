"""
Author: Nguyen Khac Thanh
"""
from typing import (
    Dict,
    Any,
    IO,
    List,
    Coroutine,
    Iterable
)
import os
import sys
import csv
import urllib
import aiohttp
import logging

from leo import _config


def read_mapping(file: IO) -> None:
    """Read mapping file for mapping sku product to MAC address
    """
    mapping: Dict[str, str] = {}

    reader = csv.reader(file)
    for row in reader:
        mapping[row[0]] = row[1]

    return mapping


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


def _make_pull_url(srv_ip: str) -> str:
    return urllib.parse.urljoin(srv_ip, _config.PRODUCT_API)


def _make_push_url(els_ip: str) -> str:
    return urllib.parse.urljoin(els_ip, _config.ELS_UPDATE_PRODUCT)


def _make_pull_product_request(skus: List[str], channel: str = 'pv_showroom',
                               terminal: int = 1) -> Dict[str, Any]:
    return {
        'channel': channel,
        'terminal': terminal,
        'skus': ','.join(skus)
    }


def _make_push_product_request(product_update: List[dict],
                               skus: List[str]) -> Dict[str, Any]:
    items = []
    for product in product_update:
        if product['sku'] in skus:
            item = {
                'Item No': product['sku'],
                'Item Name': product['name'],
                'Sell Price': product['price']['sellPrice'],
                'Sale Price': product['price']['supplierSalePrice'],
                'Other Fields': '',
                'Description': product['seoInfo']['shortDescription'],
                'Layout Index': 0,
                'action': 'M'
            }
            items.append(item)
    data = {
        'Item List': items
    }

    return data


def split(items: List[str], chuck_size: int = 10) -> Iterable:
    """Split list into chucks
    """
    while items:
        if len(items) < chuck_size:
            r_value = items
        else:
            r_value = items[:chuck_size]
        items = items[chuck_size:]
        yield r_value


async def update_coro(sess: aiohttp.ClientSession,
                      url_p_srv: str, url_els_srv: str,
                      skus: List[str]) -> Coroutine:
    """Update tags
    """
    try:
        p_res = await sess.get(
            url_p_srv,
            params=_make_pull_product_request(skus)
        )
        data = await p_res.json()
        if p_res.status != 200:
            raise aiohttp.ClientPayloadError(data['message'])
        els_res = await sess.post(
            url_els_srv,
            json=_make_push_product_request(data['result']['products'], skus)
        )
        data = await els_res.json()
        if els_res.status != 200:
            raise aiohttp.ClientError(data['ERROR'])
    except aiohttp.ClientError as err:
        logging.error(str(err))
    else:
        logging.debug('Push data success')
