# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['lvmscraper', 'lvmscraper.actor', 'lvmscraper.actor.commands']

package_data = \
{'': ['*'], 'lvmscraper': ['etc/*']}

install_requires = \
['CherryPy>=18.6.1', 'pandas>=1.4.0', 'sdss-cluplus>=0.0.18']

entry_points = \
{'console_scripts': ['container_build = container:build',
                     'container_isRunning = container:isRunning',
                     'container_start = container:start',
                     'container_stop = container:stop',
                     'lvmscraper = lvmscraper.__main__:scraper']}

setup_kwargs = {
    'name': 'sdss-lvmscraper',
    'version': '0.0.3',
    'description': 'LVM Instrument data scraper',
    'long_description': '\nlvm scraper\n==========================================\n\n|py| |pypi| |Build Status| |docs| |Coverage Status|\n\n``lvm scraper`` scraps data\n\nFeatures\n--------\n- scraps data from the rabbitmq exchange\n- simple web interface\n- creates 8key fits cards from data\n\nInstallation\n------------\n\n``lvm scraper`` can be installed using ``pip`` as\n\n.. code-block:: console\n\n    pip install sdss-lvmscraper\n\nor from source\n\n.. code-block:: console\n\n    git clone https://github.com/sdss/lvmscraper\n    cd lvmscraper\n    pip install .\n\nQuickstart\n----------\n\n.. code-block:: console\n\n    poetry run lvmscraper start\n    \nTodo\n----\n\nUsage\n-----\n\n- Start some actors\n- The actor interface has two commands data & fits with an option --filter\n\n.. code-block:: console\n\n    #> clu\n    lvm.scraper data\n    10:03:03.729 lvm.scraper >\n    10:03:03.751 lvm.scraper : {\n       ...\n    }\n    lvm.scraper data --filter lvm.*.foc\n    10:03:20.792 lvm.scraper >\n    10:03:20.858 lvm.scraper : {\n       ...\n    }\n    lvm.scraper fits\n    10:03:27.498 lvm.scraper >\n    10:03:27.507 lvm.scraper : {\n       ...\n    }\n    lvm.scraper fits --filter *.foc\n    10:03:37.945 lvm.scraper >\n    10:03:37.957 lvm.scraper : {\n      ...\n    }\n\n\n- On port 8085 there is a webserver    \n\n\n\n.. |Build Status| image:: https://img.shields.io/github/workflow/status/sdss/lvmscraper/Test\n    :alt: Build Status\n    :target: https://github.com/sdss/lvmscraper/actions\n\n.. |Coverage Status| image:: https://codecov.io/gh/sdss/lvmscraper/branch/master/graph/badge.svg?token=i5SpR0OjLe\n    :alt: Coverage Status\n    :target: https://codecov.io/gh/sdss/lvmscraper\n\n.. |py| image:: https://img.shields.io/badge/python-3.7%20|%203.8%20|%203.9-blue\n    :alt: Python Versions\n    :target: https://docs.python.org/3/\n\n.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest\n    :alt: Documentation Status\n    :target: https://lvmscraper.readthedocs.io/en/latest/?badge=latest\n\n.. |pypi| image:: https://badge.fury.io/py/sdss-lvmscraper.svg\n    :alt: PyPI version\n    :target: https://badge.fury.io/py/sdss-lvmscraper\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n',
    'author': 'Florian Briegel',
    'author_email': 'briegel@mpia.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sdss/lvmscraper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
