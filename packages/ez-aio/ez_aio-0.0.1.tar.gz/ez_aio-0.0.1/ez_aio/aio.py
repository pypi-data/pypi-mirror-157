"""
Easiest way to make get and post requests with aiohttp.
"""
from asyncio import get_event_loop, gather, sleep  # ensure_future, run
from aiohttp import ClientSession, TCPConnector
from aiohttp.typedefs import StrOrURL


async def _get(urls, binary=False, func=None, fdata=None, forced=True, ssl=False, proxy=None, headers=None,
               cookies=None):
    results = []
    i = 0
    if isinstance(urls, StrOrURL):
        urls = [urls]
    _len = len(urls)
    while True:
        try:
            async with ClientSession(connector=TCPConnector(ssl=ssl)) as session:
                if i == _len:
                    return results
                url_i = urls[i]
                async with session.get(url_i, proxy=proxy, headers=headers, cookies=cookies) as r:
                    if binary:
                        _result = await r.read()
                    else:
                        _result = await r.text()
                    if r.status == 200:
                        if func:
                            if fdata is None:
                                results.append(func(_result))
                            else:
                                results.append(func(_result, fdata[i]))
                        else:
                            results.append(_result)
                        i += 1
                    elif r.status == 403 and not forced:
                        results.append(None)
                        i += 1
                    else:
                        pass
        except Exception as e:
            print(e)


async def _post(urls, data=None, binary=False, func=None, fdata=None, forced=True, ssl=False, proxy=None, headers=None,
                cookies=None):
    results = []
    i = 0
    if isinstance(urls, StrOrURL):
        urls = [urls]
    _len = len(urls)
    if data is None:
        data = [None] * _len
    while True:
        try:
            async with ClientSession(connector=TCPConnector(ssl=ssl)) as session:
                if i == _len:
                    return results
                url = urls[i]
                data_i = data[i]
                async with session.post(url, data=data_i, proxy=proxy, headers=headers, cookies=cookies) as r:
                    if binary:
                        _result = await r.read()
                    else:
                        _result = await r.text()
                    if r.status == 200:
                        if func:
                            if fdata:
                                results.append(func(_result, fdata[i]))
                            else:
                                results.append(func(_result))
                        else:
                            results.append(_result)
                        i += 1
                    elif r.status == 403 and not forced:
                        results.append(None)
                        i += 1
                    else:
                        pass
        except Exception as e:
            print(e)


def get(urls, binary=False, func=None, fdata=None, li=99, forced=True, ssl=False, proxy=None, headers=None,
        cookies=None):
    """
    Easiest way to get with aiohttp.

    :param urls: url or list of url
    :param binary: result = response.text() if binary else response.read()
    :param func: return func(result, *) if func else return result
    :param fdata: func(result, fdata[i] if fdata else func(result)
    :param li: max of session
    :param forced: only return response.status in [200, 403] if forced
    :param ssl: ssl
    :param proxy: proxy
    :param headers: headers
    :param cookies: cookies
    :return: func(result, *) if func else result
    """
    if isinstance(urls, StrOrURL):
        urls = [urls]
    t = len(urls)
    if t < li:
        li = t
    u_lst = [urls[t * i // li:t * (i + 1) // li] for i in range(li)]
    fd_lst = [None] * li if fdata is None else [fdata[t * i // li:t * (i + 1) // li] for i in range(li)]
    tasks = [_get(u_lst[i], binary=binary, func=func, fdata=fd_lst[i], forced=forced, ssl=ssl, proxy=proxy,
                  headers=headers, cookies=cookies) for i in range(li)]
    loop = get_event_loop()
    _r = loop.run_until_complete(gather(*tasks))
    loop.run_until_complete(sleep(0))
    return [r1 for r0 in _r for r1 in r0]


def post(urls, data=None, binary=False, func=None, fdata=None, li=99, forced=True, ssl=False, proxy=None, headers=None,
         cookies=None):
    """
    Easiest way to post with aiohttp.

    :param urls: url or list of url
    :param data: post(*, data=data[i], *) Change to json=data[i] if you want.
    :param binary: result = response.text() if binary else response.read()
    :param func: return func(result, *) if func else return result
    :param fdata: func(result, fdata[i] if fdata else func(result)
    :param li: max of session
    :param forced: only return response.status in [200, 403] if forced
    :param ssl: ssl
    :param proxy: proxy
    :param headers: headers
    :param cookies: cookies
    :return: func(result, *) if func else result
    """
    if isinstance(urls, StrOrURL):
        urls = [urls]
    t = len(urls)
    if t < li:
        li = t
    u_lst = [urls[t * i // li:t * (i + 1) // li] for i in range(li)]
    fd_lst = [None] * li if fdata is None else [fdata[t * i // li:t * (i + 1) // li] for i in range(li)]
    d_lst = [None] * li if data is None else [data[t * i // li:t * (i + 1) // li] for i in range(li)]
    tasks = [_post(u_lst[i], data=d_lst[i], binary=binary, func=func, fdata=fd_lst[i], forced=forced, ssl=ssl,
                   proxy=proxy, headers=headers, cookies=cookies) for i in range(li)]
    loop = get_event_loop()
    _r = loop.run_until_complete(gather(*tasks))
    loop.run_until_complete(sleep(0))
    return [r1 for r0 in _r for r1 in r0]
