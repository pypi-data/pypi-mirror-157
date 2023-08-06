# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mystbin']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['aiohttp>=3.7.4,<4.0.0']

extras_require = \
{'docs': ['sphinx>=4.0.0,<5.0.0', 'sphinxcontrib-trio', 'furo'],
 'requests': ['requests>=2.24.0,<3.0.0']}

entry_points = \
{'console_scripts': ['version = mystbin.__main__:show_version']}

setup_kwargs = {
    'name': 'mystbin.py',
    'version': '4.0.2',
    'description': 'A small simple wrapper around the mystb.in API.',
    'long_description': '<div align="center">\n    <h1>Mystbin.py!</h1>\n    <a href=\'https://mystbinpy.readthedocs.io/en/latest/?badge=latest\'>\n        <img src=\'https://readthedocs.org/projects/mystbinpy/badge/?version=latest\' alt=\'Documentation Status\' />\n    </a>\n    <a href=\'https://github.com/AbstractUmbra/mystbin.py/workflows/Code%20Linting\'>\n        <img src=\'https://github.com/AbstractUmbra/mystbin.py/workflows/Code%20Linting/badge.svg?branch=main\' alt=\'Linting status\' />\n    </a>\n    <a href=\'https://github.com/AbstractUmbra/mystbin.py/workflows/Build\'>\n        <img src=\'https://github.com/AbstractUmbra/mystbin.py/workflows/Build/badge.svg\' alt=\'Build status\' />\n    </a>\n</div>\n<br>\n\nA small simple wrapper around the [MystB.in](https://mystb.in/) API.\n----------\n### Features\n\n- [x] - `POST`ing to the API, which will return the provided url.\n- [x] - `GET`ting from the API, provided you know the URL or paste ID.\n- [ ] - `DELETE`ing from the API, provided the paste is attached to your account.\n- [ ] - `PATCH`ing to the API, provided the paste is attached to your account.\n- [x] - Ability to pass in a sync or async session / parameter so it is flexible.\n- [x] - Write a real underlying Client for this, it will be required for...\n- [ ] - ... Authorization. Awaiting the API making this public as it is still WIP.\n\n### Installation\nThis project will be on [PyPI](https://pypi.org/project/mystbin.py/) as a stable release, you can always find that there.\n\nInstalling via `pip`:\n```shell\npython -m pip install -U mystbin.py\n# or for optional sync addon...\npython -m pip install -U mystbin.py[requests]\n```\n\nInstalling from source:\n```shell\npython -m pip install git+https://github.com/AbstractUmbra/mystbin-py.git #[requests] for sync addon\n```\n\n### Usage examples\nSince the project is considered multi-sync, it will work in a sync/async environment, see the optional dependency of `requests` below.\n\n```py\n# async example - it will default to async\nimport mystbin\n\nmystbin_client = mystbin.Client()\n\npaste = await mystbin_client.post("Hello from MystBin!", syntax="python")\nstr(paste)\n>>> \'https://mystb.in/<your generated ID>.python\'\n\npaste.url\n>>> \'https://mystb.in/<your generated ID>.python\'\n\nget_paste = await mystbin_client.get("https://mystb.in/<your generated ID>")\nstr(get_paste)\n>>> "Hello from MystBin!"\n\npaste.created_at\n>>> datetime.datetime(2020, 10, 6, 10, 53, 57, 556741)\n```\n\n```py\nimport mystbin\n\nmystbin_client = mystbin.SyncClient()\n\npaste = mystbin_client.post("Hello from sync Mystb.in!", syntax="text")\nstr(paste)\n>>> \'https://mystb.in/<your generated ID>.text\'\n```\n\nNOTE: There is a timeout of 15s for each operation.\n',
    'author': 'AbstractUmbra',
    'author_email': 'Umbra@AbstractUmbra.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AbstractUmbra/mystbin-py',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
