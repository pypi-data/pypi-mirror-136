# requests-default
## Info
This set default `requests <https://docs.python-requests.org/en/latest/>`_'s `url`, `headers` etc...

```python
from requests_base import DefaultSession
    session = DefaultSession(base_url='https://example.com/resource/', headers={'api-key': 'aabbcc'})
    r = session.get('sub-resource/', params={'foo': 'bar'})
    print(r.request.url)
```

## License
Distributed under the terms of the MIT license, pytest is free and open source software.