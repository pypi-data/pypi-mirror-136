# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_modified_env']

package_data = \
{'': ['*']}

entry_points = \
{'pytest11': ['pytest_modified_env = pytest_modified_env.plugin']}

setup_kwargs = {
    'name': 'pytest-modified-env',
    'version': '0.1.0',
    'description': 'Pytest plugin to fail a test if it leaves modified `os.environ` afterwards.',
    'long_description': "# pytest-modified-env\n\n[![Build Status](https://github.com/wemake-services/pytest-modified-env/workflows/test/badge.svg?branch=master&event=push)](https://github.com/wemake-services/pytest-modified-env/actions?query=workflow%3Atest)\n[![Python Version](https://img.shields.io/pypi/pyversions/pytest-modified-env.svg)](https://pypi.org/project/pytest-modified-env/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nPytest plugin to fail a test if it leaves modified `os.environ` afterwards.\n\nExample:\n\n```python\nimport os\n\ndef test_that_modifies_env() -> None:\n    os.environ['CUSTOM_ENV'] = '1'\n```\n\nWith `pytest-modified-env` plugin installed, this test will fail:\n\n```\n___________________________ test_that_modifies_env ____________________________\ntest_that_modifies_env:4: in pytest_runtest_call\nE   RuntimeError: os.environ was changed\n```\n\nBecause it adds `CUSTOM_ENV` inside a test and does not clean it up.\nIn theory it can affect other tests and tests should be isolated!\n\n\n## Installation\n\n```bash\npip install pytest-modified-env\n```\n\n\n## Extras\n\nIn some cases test still might modify the env in this way. \nBut, it needs an explicit approval for that:\n\n```python\nimport os\nimport pytest\n\n@pytest.mark.modify_env()\ndef test_that_modifies_env() -> None:\n    os.environ['CUSTOM_ENV'] = '1'\n```\n\nThis test won't fail, eventhough it adds `CUSTOM_ENV`,\nbecause it has `modifies_env` marker.\n\n\n## License\n\n[MIT](https://github.com/wemake-services/pytest-modified-env/blob/master/LICENSE)\n",
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wemake-services/pytest-modified-env',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
