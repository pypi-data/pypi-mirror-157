# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['howdyho']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['howdyho = howdyho:while_true_print_howdyho_help']}

setup_kwargs = {
    'name': 'howdyho',
    'version': '3.0.1',
    'description': 'Забавный скрипт, без остановки печатающий фразу "Хаудихо помоги".',
    'long_description': '# Howdyho\n~~Бесполезный~~ Забавный скрипт, без остановки печатающий фразу "Хаудихо помоги".\n\n# Установка\n```shell\npip install -U howdyho\n```\n\n# Использование\n```shell\nhowdyho\n# или\npython -m howdyho\n```\n',
    'author': 'Voronin9032',
    'author_email': 'voronin9032n3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/voronin9032/howdyho',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
