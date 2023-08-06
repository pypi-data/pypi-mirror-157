# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_patterns', 'py_patterns.adapters']

package_data = \
{'': ['*']}

install_requires = \
['absl-py>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'py-patterns-util',
    'version': '0.1.0',
    'description': 'A util library for common patterns in python.',
    'long_description': '# py-patterns\n\nA util library for common patterns in python.\n\n## Supported patterns\n\n1. Adapters\n\n## Example\n\n```py\nfrom py_patterns.adapters import Field, Adapter\n\n\nclass PersonAdapter(Adapter):\n    last_name = Field(source="person.last_name", dtype=str)\n    first_name = Field(source="person.first_name", dtype=str)\n    age = Field(source="person.age", dtype=int)\n\n\nsource_data = {"person": {"last_name": "Smith", "first_name": "John", "age": 30}}\n\n# {"last_name": "Smith", "first_name": "John", "age": 30}\nconverted_data = PersonAdapter(source_data=source_data).convert()\n```\n',
    'author': 'Priyanshu Jain',
    'author_email': 'ipriyanshujain@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/priyanshujain/py-patterns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
