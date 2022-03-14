import sys, time, contextlib

# https://stackoverflow.com/a/8290508
def batches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0,l,n):
        yield iterable[ndx:min(ndx + n, l)]

def flatten(nested):
    for iterable in nested:
        yield from iterable

# https://stackoverflow.com/a/46217079
def partition(p, l):
    x = [], []
    for n in l: x[p(n)].append(n)
    return x

@contextlib.contextmanager
def warn(*exceptions, func=''):
    try:
        yield
    except exceptions as ex:
        print(func, type(ex), ex, file=sys.stderr)

from contextlib import suppress

timeout = 60
import asyncio

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    
    from functools import wraps
    from asyncio.proactor_events import _ProactorBasePipeTransport

    def silence_event_loop_closed(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if str(e) != 'Event loop is closed':
                    raise
        return wrapper

    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

    
# https://stackoverflow.com/a/63179518
def async_get_all(urls, timeout=timeout, max_size=1000000, **kwargs):
    """
    performs asynchronous get requests
    """
    from aiohttp import ClientSession, ClientTimeout
    from asgiref import sync

    async def get_all(urls):
        client_timeout = ClientTimeout(total=None, sock_connect=timeout, sock_read=timeout)
        async with ClientSession(timeout=client_timeout) as session:
            async def fetch(url):
                text = b''
                with warn(Exception), warn(asyncio.TimeoutError):
                    async with session.get(url, **kwargs) as response:
                        length = response.headers.get('Content-Length')
                        if length and int(length) > max_size:
                            raise ValueError('response too large')
                        size = 0
                        start = time.time()

                        async for chunk in response.content.iter_chunked(1024):
                            if time.time() - start > timeout:
                                raise ValueError('timeout reached')
                            size += len(chunk)
                            if size > max_size:
                                raise ValueError('response too large')

                            text += chunk
                return text
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    # call get_all as a sync function to be used in a sync context
    return sync.async_to_sync(get_all)(urls)

def sync_get_all(urls, wait=1, timeout=timeout, **kwargs):
    import requests
    import cchardet
    import time
    session = requests.Session()
    for url in urls:
        text = b''
        with warn(Exception), suppress(requests.exceptions.ReadTimeout):
            # https://thehftguy.com/2020/07/28/making-beautifulsoup-parsing-10-times-faster/
            response = session.get(url, timeout=timeout, verify=True, **kwargs)
            #response.raw.decode_content = True
            text = response.content
            time.sleep(wait)
        yield text

def async_download_get_all(urls, paths, timeout=timeout, max_size=1000000, **kwargs):
    """
    performs asynchronous get requests
    """
    from aiohttp import ClientSession, ClientTimeout
    from asgiref import sync
    import aiofiles

    async def get_all(urls):
        client_timeout = ClientTimeout(total=None, sock_connect=timeout, sock_read=timeout)
        async with ClientSession(timeout=client_timeout) as session:
            async def fetch(url, path):
                try:
                    async with session.get(url, **kwargs) as response:
                        length = response.headers.get('Content-Length')
                        if length and int(length) > max_size:
                            raise ValueError('response too large')
                        size = 0
                        start = time.time()
                        
                        async with aiofiles.open(path, mode='wb') as f:
                            async for chunk in response.content.iter_chunked(1024):
                                if time.time() - start > timeout:
                                    raise ValueError('timeout reached')
                                size += len(chunk)
                                if size > max_size:
                                    raise ValueError('response too large')

                                await f.write(chunk)
                except Exception as ex:
                    return ex
                return True
            return await asyncio.gather(*[
                fetch(url, path) for url, path in zip(urls, paths)
            ])
    # call get_all as a sync function to be used in a sync context
    return sync.async_to_sync(get_all)(urls)