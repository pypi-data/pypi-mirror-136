# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['requests_default']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=2.12.2,<3.0.0', 'requests>=2.16.0,<3.0.0']

setup_kwargs = {
    'name': 'requests-default',
    'version': '0.1.1',
    'description': 'Request for default',
    'long_description': "# requests-default\n## Info\nThis set default `requests <https://docs.python-requests.org/en/latest/>`_'s `url`, `headers` etc...\n\n```python\nfrom requests_base import DefaultSession\n    session = DefaultSession(base_url='https://example.com/resource/', headers={'api-key': 'aabbcc'})\n    r = session.get('sub-resource/', params={'foo': 'bar'})\n    print(r.request.url)\n```\n\n## License\nDistributed under the terms of the MIT license, pytest is free and open source software.",
    'author': 'geonwoo.kim',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ultimatelife/requests-default',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
