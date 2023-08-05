# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['disnakedb']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'disnakedb',
    'version': '0.1.1',
    'description': 'Easy and fast db for python users',
    'long_description': '# disnakedb\n\n## Installation\n\n```\npip3 install disnakedb\n```\n\n## Usage\n```python\nimport disnakedb\n\ndb = fast_db.Init()\n\nprint(db.get("foo"))  # None\n\ndb.set("foo", "bar")\nprint(db.get("foo"))  # bar\n\ndb.set("any", {"id": 1234, "top": 1, "str": "any string"})\nprint(db.get("any"))  # {"id": 1234, "top": 1, "str": "any string"}\nprint(db.get("any")["id"])  # 1234\n\ndb.remove("foo")\ndb.remove("any")\nprint(db.get("foo"))  # None\n\n```',
    'author': 'Hawchik',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
