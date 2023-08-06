# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rag',
 'rag.cli',
 'rag.cli.commands',
 'rag.core',
 'rag.core.middleware',
 'rag.core.settings',
 'rag.patches',
 'rag.signals',
 'rag.tasks',
 'rag.templates.large',
 'rag.templates.large.api',
 'rag.templates.large.api.migrations',
 'rag.templates.large.api.models',
 'rag.templates.large.api.routes',
 'rag.templates.large.settings',
 'rag.templates.large.tests',
 'rag.templates.large.tests.models',
 'rag.templates.large.tests.routes',
 'rag.templates.medium',
 'rag.templates.medium.api',
 'rag.templates.medium.api.migrations',
 'rag.templates.medium.tests',
 'rag.templates.micro',
 'rag.templates.small',
 'rag.templates.small.migrations',
 'rag.test',
 'rag.validation',
 'rag.validation.acceptors',
 'rag.validation.converters',
 'rag.validation.skippers',
 'rag.validation.validators']

package_data = \
{'': ['*'], 'rag': ['templates/*'], 'rag.templates.large': ['static/*']}

install_requires = \
['Django',
 'celery>=5.0.2,<6.0.0',
 'channels-redis>=3.2.0,<4.0.0',
 'channels>=3.0.2,<4.0.0',
 'daphne>=3.0.1,<4.0.0',
 'django-extensions>=3.0.9,<4.0.0',
 'ipython>=7.19.0,<8.0.0',
 'pylint>=2.7.2,<3.0.0',
 'pytest-django>=4.1.0,<5.0.0',
 'pytest-mock>=3.3.1,<4.0.0',
 'pytest>=6,<7',
 'python-dateutil>=2.8.1,<3.0.0',
 'ragclip>=0.0.4,<0.0.5',
 'redis>=3.5.3,<4.0.0',
 'watchdog>=0.10.3,<0.11.0']

setup_kwargs = {
    'name': 'rag',
    'version': '0.0.20',
    'description': '',
    'long_description': '# Rag\n*Make creating rest APIs in Django simple.*\n\nRag is a simple batteries included tool to make building rest API\'s using Django fast and easy.\n\n## Usage\n\n#### Quick Start\n\n#### Command Line\nThe command line interface has commands to start a dev server, run development shell, run tests, run Django management commands, create an empty example project, and run a Celery background task worker.\n\n#### Validation\n  To validate a field you must start with a root validator: `to`, `am`, `accepts`, or `optional`.  All root\n  validators check that a field is defined before proceeding with the exception of `optional` which will\n  immediately accept if the field is undefined on the json object.\n\n## Contributing\n\n#### Lauching Dev Stack\nUse docker compose to launch development stack.\n\n#### Dev Setup\nTo install development requirements.\n`poetry install`\n\n#### Running Dev Tests\nTo run tests:  \n`poetry run poe test`\n\nTo run a specific test or test file:  \n`poetry run poe test -k test_rag.py`\n\nTo run a specific test in a suite:  \n`poetry run poe test -k "test_validate.py and test_check"`\n\nTo see all print statements of passing tests use the `-s` flag\n`poetry run poe test -s`\n\nTo run tests with auto reload:  \n`poetry run poe test-watch`\n\nTo run tests with auto reload and specific test:  \n`poetry run poe test-watch -k test_name`\n\n\nNote: Errors like this might have a root exception with more detail and may mean you are missing migrations:\n`psycopg2.errors.InvalidCursorName`\n',
    'author': 'Mark Raleson',
    'author_email': 'markraleson@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mraleson/rag.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
