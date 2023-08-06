# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cookiecutter_poetry_example']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cookiecutter-poetry-example',
    'version': '0.3.6',
    'description': 'This is a template repository for Python projects that use Poetry for their dependency management.',
    'long_description': '# cookiecutter-poetry-example\n\n[![Release](https://img.shields.io/github/v/release/fpgmaas/cookiecutter-poetry-example)](https://img.shields.io/github/v/release/fpgmaas/cookiecutter-poetry-example)\n[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/cookiecutter-poetry-example/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/cookiecutter-poetry-example/merge-to-main)\n[![Commit activity](https://img.shields.io/github/commit-activity/m/fpgmaas/cookiecutter-poetry-example)](https://img.shields.io/github/commit-activity/m/fpgmaas/cookiecutter-poetry-example)\n[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://fpgmaas.github.io/cookiecutter-poetry-example/)\n[![Code style with black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports with isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/)\n[![License](https://img.shields.io/github/license/fpgmaas/cookiecutter-poetry-example)](https://img.shields.io/github/license/fpgmaas/cookiecutter-poetry-example)\n\nThis is a template repository for Python projects that use Poetry for their dependency management.\n\n- **Github repository**: <https://github.com/fpgmaas/cookiecutter-poetry-example/>\n- **Documentation** <https://fpgmaas.github.io/cookiecutter-poetry-example/>\n\n## Releasing a new version\n\n- Create an API Token on [Pypi](https://pypi.org/).\n- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting \n[this page](https://github.com/fpgmaas/cookiecutter-poetry-example/settings/secrets/actions/new).\n- Create a [new release](https://github.com/fpgmaas/cookiecutter-poetry-example/releases/new) on Github. \nCreate a new tag in the form ``*.*.*``.\n\nFor more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/releasing.html).\n\n---\n\nRepository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).',
    'author': 'Florian Maas',
    'author_email': 'ffpgmaas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fpgmaas/cookiecutter-poetry-example',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
