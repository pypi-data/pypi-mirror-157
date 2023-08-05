# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['radio_mlbee']

package_data = \
{'': ['*'], 'radio_mlbee': ['data/*']}

install_requires = \
['aset2pairs>=0.1.0,<0.2.0',
 'cchardet>=2.1.7,<3.0.0',
 'cmat2aset>=0.1.0-alpha.7,<0.2.0',
 'gradio>=3.0.15,<4.0.0',
 'hf-model-s-cpu>=0.1.1,<0.2.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'joblib>=1.1.0,<2.0.0',
 'logzero>=1.7.0,<2.0.0',
 'more-itertools>=8.13.0,<9.0.0',
 'seg-text>=0.1.2,<0.2.0',
 'sentence-transformers>=2.2.0,<3.0.0',
 'set-loglevel>=0.1.2,<0.2.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['radio-mlbee = radio_mlbee.__main__:app']}

setup_kwargs = {
    'name': 'radio-mlbee',
    'version': '0.1.0a2',
    'description': 'mlbee via gradio',
    'long_description': '---\ntitle: Radio Mlbee\nemoji: 💻\ncolorFrom: gray\ncolorTo: red\nsdk: gradio\nsdk_version: 3.0.15\napp_file: app.py\npinned: false\nlicense: mit\n---\n\n# radio-mlbee\n[![pytest](https://github.com/ffreemt/radio-mlbee/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/radio-mlbee/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/radio_mlbee.svg)](https://badge.fury.io/py/radio_mlbee)\n\nmlbee via gradio\n\n## Install it\n\n```shell\npip install git+https://github.com/ffreemt/radio-mlbee\n# poetry add git+https://github.com/ffreemt/radio-mlbee\n# git clone https://github.com/ffreemt/radio-mlbee && cd radio-mlbee\n```\n\n## Use it\n```python\nfrom radio_mlbee import radio_mlbee\n\n```\n=======\nCheck out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/radio-mlbee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
