# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_test_database']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.0,<4.0']

setup_kwargs = {
    'name': 'fast-test-database',
    'version': '0.1.3',
    'description': 'Configure an in-memory database for running Django tests',
    'long_description': "Fast test database\n==================\n\nUse a pure in-memory database for running Django tests.\n\nUsage\n-----\n\nIn ``settings.py``:\n\n.. code:: python\n\n    from fast_test_database import fast_test_database\n\n    DATABASES = fast_test_database(DATABASES)\n\n    # Or:\n    DATABASES = fast_test_database(DATABASES,\n                                   test_commands=('test', 'harvest'))\n\n    # Or:\n    DATABASES = fast_test_database(DATABASES,\n                                   version='5.7')\n\nThis will be a no-op except for ``./manage.py test``, when an in-memory\ndatabase will be automatically started and supplied to the application.\n\nDetails\n-------\n\nThe in-memory database is a full PostgreSQL or MySQL instance started\nusing Docker, using tmpfs for storing the data. A single container will\nbe started if not yet running. It will not be shut down automatically,\nand instead reused for subsequent tests.\n\nThe type of the database (PostgreSQL or MySQL) is chosen based on the\nexisting default database engine.\n\nThe default version of the database (PostgreSQL or MySQL) is latest.\nBut it can be specified by version parameter.\n",
    'author': 'Alexey Kotlyarov',
    'author_email': 'a@koterpillar.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
