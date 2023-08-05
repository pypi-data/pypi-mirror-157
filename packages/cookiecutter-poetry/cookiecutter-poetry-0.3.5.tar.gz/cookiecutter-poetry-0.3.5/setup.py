# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cookiecutter_poetry']

package_data = \
{'': ['*']}

install_requires = \
['cookiecutter>=1.7.3,<2.0.0']

entry_points = \
{'console_scripts': ['ccp = cookiecutter_poetry.cli:main']}

setup_kwargs = {
    'name': 'cookiecutter-poetry',
    'version': '0.3.5',
    'description': 'A python cookiecutter application to create a new python project that uses poetry to manage its dependencies.',
    'long_description': '# Cookiecutter Poetry\n\n[![Release](https://img.shields.io/github/v/release/fpgmaas/cookiecutter-poetry)](https://pypi.org/project/cookiecutter-poetry/)\n[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/cookiecutter-poetry/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/cookiecutter-poetry/merge-to-main)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/cookiecutter-poetry)](https://pypi.org/project/cookiecutter-poetry/)\n[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://fpgmaas.github.io/cookiecutter-poetry/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/cookiecutter-poetry)](https://img.shields.io/pypi/dm/cookiecutter-poetry?style=flat-square)\n[![License](https://img.shields.io/github/license/fpgmaas/cookiecutter-poetry)](https://img.shields.io/github/license/fpgmaas/cookiecutter-poetry)\n\n\nThis is a [cookiecutter](https://github.com/cookiecutter/cookiecutter)\nrepository to generate the file structure for a Python project that uses\n[Poetry](https://python-poetry.org/) for its dependency management.\n\n- **Documentation**: [Link](https://fpgmaas.github.io/cookiecutter-poetry/)\n- **Example repository**: [Link](https://github.com/fpgmaas/cookiecutter-poetry-example)\n- **PyPi**: [Link](https://pypi.org/project/cookiecutter-poetry/)\n\n## Features\n\n- [Poetry](https://python-poetry.org/), obviously.\n- CI/CD with [GitHub Actions](https://github.com/features/actions)\n- Formatting with [black](https://pypi.org/project/black/) and [isort](https://pycqa.github.io/isort/index.html)\n- Linting with [flake8](https://flake8.pycqa.org/en/latest/)\n- Publishing to [Pypi](https://pypi.org) or [Artifactory](https://jfrog.com/artifactory) by creating a new release on GitHub\n- Testing with [pytest](https://docs.pytest.org/en/7.1.x/)\n- Documentation with [MkDocs](https://www.mkdocs.org/)\n- Static type checking with [mypy](https://mypy.readthedocs.io/en/stable/)\n- Compatibility testing for multiple versions of Python with [Tox](https://tox.wiki/en/latest/)\n- Containerization with [Docker](https://www.docker.com/)\n\n## Example CI/CD Pipeline\n\n[![Example pipeline](https://raw.githubusercontent.com/fpgmaas/cookiecutter-poetry/main/static/images/pipeline.png)](https://raw.githubusercontent.com/fpgmaas/cookiecutter-poetry/main/static/images/pipeline.png)\n\n## Quickstart\n\nOn your local machine, navigate to the directory in which you want to\ncreate a project directory, and run the following two commands:\n\n``` bash\npip install cookiecutter-poetry \nccp\n```\n\nAlternatively, install `cookiecutter` and directly pass the URL to this\nGithub repository to the `cookiecutter` command:\n\n``` bash\npip install cookiecutter\ncookiecutter https://github.com/fpgmaas/cookiecutter-poetry.git\n```\n\nThen run the following commands, replacing `<project-name>`, with the\nname that you also gave the Github repository and\n`<github_author_handle>` with your Github username.\n\n``` bash\ncd <project_name>\ngit init -b main\ngit add .\ngit commit -m "Init commit"\ngit remote add origin git@github.com:<github_author_handle>/<project_name>.git\ngit push -u origin main\n```\n\nFinally, install the environment with `make install`.\n\nYou are now ready to start development on your project! The CI/CD\npipeline will be triggered when you open a pull request, merge to main,\nor when you create a new release.\n\nTo finalize the set-up for publishing to PyPi or Artifactory, see\n[here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).\nFor activating the automatic documentation with MkDocs, see\n[here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).\n\n## Acknowledgements\n\nThis project is partially based on [Audrey\nFeldroy\\\'s](https://github.com/audreyfeldroy)\\\'s great\n[cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage)\nrepository.\n',
    'author': 'Florian Maas',
    'author_email': 'fpgmaas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fpgmaas/cookiecutter-poetry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
