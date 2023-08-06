"""
A Requests Session with a base URL.
"""
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Optional, Dict

import requests
from requests.adapters import HTTPAdapter
from requests.cookies import cookiejar_from_dict
from requests.hooks import default_hooks
from requests.models import DEFAULT_REDIRECT_LIMIT
from requests.utils import default_headers
from requests.auth import AuthBase


class DefaultSession(requests.Session):
    """
    A Requests Session with a URL that all requests will use as a base.

    Let's start by looking at an example:
    .. code-block:: python
        # >>> from requests_base import DefaultSession
        >>> session = DefaultSession(base_url='https://example.com/resource/', headers={'api-key': 'aabbcc'})
        >>> r = session.get('sub-resource/', params={'foo': 'bar'})
        >>> print(r.request.url)
    """

    def __init__(self, url: Optional[str] = None, params: Dict[Any, Any] = {}, headers: Dict[Any, Any] = {},
                 cookies: Dict[Any, Any] = {}, timeout: Optional[int] = None, allow_redirects: bool = True,
                 auth: Optional[AuthBase] = None) -> None:
        self.url = url

        self.headers = default_headers()
        self.headers.update(headers)

        self.auth = auth

        self.proxies = {}

        #: Event-handling hooks.
        self.hooks = default_hooks()

        self.params = params
        self.params.update(params)

        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        self.trust_env = True

        self.cookies = cookiejar_from_dict({})
        self.cookies.update(cookies)

        self.adapters = OrderedDict()

        self.mount('https://', HTTPAdapter())

        self.mount('http://', HTTPAdapter())

        self.timeout = timeout
        self.allow_redirects = allow_redirects

    def request(self, method: str, url: str, *args: Any, **kwargs: Any, ) -> requests.models.Response:
        url = f'{self.url}{url}'

        for k in {'params', 'headers', 'cookies'}:
            if k in kwargs:
                # append
                kwargs[k], temp = deepcopy(getattr(self, k)), kwargs[k]
                kwargs[k].update(temp)
            elif getattr(self, k):
                # overwrite
                kwargs[k] = getattr(self, k)

        # overwrite
        for k in {'timeout', 'allow_redirects', 'auth'}:
            if k not in kwargs and self.timeout:
                kwargs[k] = getattr(self, k)

        return super().request(
            method=method,
            url=url,
            *args,
            **kwargs,
        )
