# Based on https://github.com/mansuf/zippyshare-downloader/blob/main/zippyshare_downloader/network.py

import requests
import aiohttp
import asyncio
import time
import logging
import sys
from . import __version__

log = logging.getLogger(__name__)

__all__ = (
    'Net', 'NetworkObject',
    'set_proxy', 'clear_proxy',
    'base_url', 'uploads_url'
)

base_url = 'https://api.mangadex.org'
uploads_url = 'https://uploads.mangadex.org'

# Modified requests session class with __del__ handler
# so the session will be closed properly
class requestsMangaDexSession(requests.Session):
    def __init__(self, trust_env=True) -> None:
        super().__init__()
        self.trust_env = trust_env
        user_agent = 'mangadex-downloader (https://github.com/mansuf/mangadex-downloader {0}) '.format(__version__)
        user_agent += 'Python/{0[0]}.{0[1]} '.format(sys.version_info)
        user_agent += 'aiohttp/{0} requests/{1}'.format(
            aiohttp.__version__,
            requests.__version__
        )
        self.headers = {
            "User-Agent": user_agent
        }

    # Ratelimit handler
    def request(self, *args, **kwargs):
        attempt = 1
        while True:
            resp = super().request(*args, **kwargs)

            # We are being rate limited
            if resp.status_code == 429:

                # x-ratelimit-retry-after is from MangaDex and
                # Retry-After is from DDoS-Guard
                if resp.headers.get('x-ratelimit-retry-after'):
                    delay = float(resp.headers.get('x-ratelimit-retry-after')) - time.time()
                
                elif resp.headers.get('Retry-After'):
                    delay = float(resp.headers.get('Retry-After'))
                
                log.info('We being rate limited, sleeping for %0.2f (attempt: %s)' % (delay, attempt))
                time.sleep(delay)
                attempt += 1
                continue

            return resp


# Because aiohttp doesn't support proxy from session
# we need to subclass it to proxy each requests without
# add "proxy" parameter to each requests
class aiohttpProxiedSession(aiohttp.ClientSession):
    def __init__(self, proxy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy = proxy

    def set_proxy(self, proxy):
        self.proxy = proxy
    
    def remove_proxy(self):
        self.proxy = None

    async def _request(self, *args, **kwargs):
        kwargs.update(proxy=self.proxy)
        return await super()._request(*args, **kwargs)

class NetworkObject:
    def __init__(self, proxy=None, trust_env=False) -> None:
        self._proxy = proxy
        self._aiohttp = None # type: aiohttpProxiedSession
        self._trust_env = trust_env

        # This will be disable proxy from environtments
        self._requests = None

    @property
    def proxy(self):
        """Return HTTP/SOCKS proxy, return ``None`` if not configured"""
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        self.set_proxy(proxy)

    @property
    def trust_env(self):
        """Return ``True`` if http/socks proxy are grabbed from env"""
        return self._trust_env

    @trust_env.setter
    def trust_env(self, yes):
        self._trust_env = yes
        if self._aiohttp:
            self._aiohttp._trust_env = yes
        if self._requests:
            self._requests.trust_env = yes

    def is_proxied(self):
        """Return ``True`` if requests/aiohttp from :class:`NetworkObject`
        are configured using proxy.
        """
        return self.proxy is not None

    def set_proxy(self, proxy):
        """Setup HTTP/SOCKS proxy for aiohttp/requests"""
        if not proxy:
            self.clear_proxy()
        self._proxy = proxy
        if self._requests:
            self._update_requests_proxy(proxy)
        if self._aiohttp:
            self._update_aiohttp_proxy(proxy)

    def clear_proxy(self):
        """Remove all proxy from aiohttp/request and disable environments proxy"""
        self._proxy = None
        self._trust_env = False
        if self._requests:
            self._requests.proxies.clear()
            self._requests.trust_env = False
        if self._aiohttp:
            self._aiohttp.remove_proxy()
            self._aiohttp._trust_env = False

    def _update_aiohttp_proxy(self, proxy):
        if self._aiohttp:
            self._aiohttp.set_proxy(proxy)
            self._aiohttp._trust_env = self._trust_env

    @property
    def aiohttp(self):
        """Return proxied aiohttp (if configured)"""
        self._create_aiohttp()
        return self._aiohttp

    def _update_requests_proxy(self, proxy):
        if self._requests:
            pr = {
                'http': proxy,
                'https': proxy
            }
            self._requests.proxies.update(pr)
            self._requests.trust_env = self._trust_env

    def _create_requests(self):
        if self._requests is None:
            self._requests = requestsMangaDexSession(self._trust_env)
            self._update_requests_proxy(self.proxy)

    @property
    def requests(self):
        """Return proxied requests (if configured)"""
        self._create_requests()
        return self._requests

    def _create_aiohttp(self):
        # Check if current asyncio loop is running
        # if running create aiohttp session
        # if not don't create it
        loop = asyncio.get_event_loop()

        # Raise error if using in another thread
        if self._aiohttp and self._aiohttp._loop != loop:
            raise RuntimeError('created aiohttp session cannot be used in different thread')

        if self._aiohttp is None:
            self._aiohttp = aiohttpProxiedSession(self.proxy)
            self._update_aiohttp_proxy(self.proxy)

    def close(self):
        """Close requests session only"""
        self._requests.close()
        self._requests = None

    async def close_async(self):
        """Close aiohttp & requests session"""
        self.close()
        if not self._aiohttp.closed:
            await self._aiohttp.close()
        self._aiohttp = None

Net = NetworkObject()

def set_proxy(proxy):
    """Setup HTTP/SOCKS proxy for aiohttp/requests
    
    This is shortcut for :meth:`NetworkObject.set_proxy`.
    This will apply to ``Net`` object globally.
    """
    Net.set_proxy(proxy)

def clear_proxy():
    """Remove all proxy from aiohttp/requests
    
    This is shortcut for :meth:`NetworkObject.clear_proxy`. 
    This will apply to ``Net`` object globally.
    """
    Net.clear_proxy()