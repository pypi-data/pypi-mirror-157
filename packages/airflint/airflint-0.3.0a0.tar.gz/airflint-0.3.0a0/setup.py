# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['airflint', 'airflint.actions', 'airflint.rules']

package_data = \
{'': ['*']}

install_requires = \
['refactor>=0.4.3,<0.5.0']

entry_points = \
{'console_scripts': ['airflint = airflint.__main__:main']}

setup_kwargs = {
    'name': 'airflint',
    'version': '0.3.0a0',
    'description': 'Enforce Best Practices for all your Airflow DAGs. ⭐',
    'long_description': '# airflint\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/feluelle/airflint/main.svg)](https://results.pre-commit.ci/latest/github/feluelle/airflint/main)\n![test workflow](https://github.com/feluelle/airflint/actions/workflows/test.yml/badge.svg)\n![codeql-analysis workflow](https://github.com/feluelle/airflint/actions/workflows/codeql-analysis.yml/badge.svg)\n[![codecov](https://codecov.io/gh/feluelle/airflint/branch/main/graph/badge.svg?token=J8UEP8IVY4)](https://codecov.io/gh/feluelle/airflint)\n[![PyPI version](https://img.shields.io/pypi/v/airflint)](https://pypi.org/project/airflint/)\n[![License](https://img.shields.io/pypi/l/airflint)](https://github.com/feluelle/airflint/blob/main/LICENSE)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflint)](https://pypi.org/project/airflint/)\n[![PyPI version](https://img.shields.io/pypi/dm/airflint)](https://pypi.org/project/airflint/)\n\n> Enforce Best Practices for all your Airflow DAGs. ⭐\n\n## 🧑\u200d🏫 Rules\n\n- [x] Use function-level imports instead of top-level imports[^1][^2] (see [Top level Python Code](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#top-level-python-code))\n- [x] Use jinja macro instead of `Variable.get` (see [Airflow Variables](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#airflow-variables))\n\n[^1]: There is a PEP for [Lazy Imports](https://peps.python.org/pep-0690/) targeted to arrive in Python 3.12 which would supersede this rule.\n\n[^2]: To remove top-level imports after running `UseFunctionLevelImports` rule, use a tool such as [autoflake](https://github.com/PyCQA/autoflake).\n\n_based on official [Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)_\n\n## 🚀 Get started\n\nTo install it from [PyPI](https://pypi.org/) run:\n\n```console\npip install airflint\n```\n\n> **_NOTE:_** It is recommended to install airflint into your existing airflow environment with all your providers included. This way `UseJinjaVariableGet` rule can detect all `template_fields` and airflint works as expected.\n\nThen just call it like this:\n\n![usage](assets/images/usage.png)\n\n### pre-commit\n\nAlternatively you can add the following repo to your `pre-commit-config.yaml`:\n\n```yaml\n  - repo: https://github.com/feluelle/airflint\n    rev: v0.3.0-alpha\n    hooks:\n      - id: airflint\n        args: ["-a"]  # Use -a for replacing inplace\n        additional_dependencies:  # Add all package dependencies you have in your dags, preferable with version spec\n          - apache-airflow\n          - apache-airflow-providers-cncf-kubernetes\n```\n\nTo complete the `UseFunctionlevelImports` rule, please add the `autoflake` hook after the `airflint` hook, as below:\n\n```yaml\n  - repo: https://github.com/pycqa/autoflake\n    rev: v1.4\n    hooks:\n      - id: autoflake\n        args: ["--remove-all-unused-imports", "--in-place"]\n```\n\nThis will remove unused imports.\n',
    'author': 'Felix Uellendall',
    'author_email': 'feluelle@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
