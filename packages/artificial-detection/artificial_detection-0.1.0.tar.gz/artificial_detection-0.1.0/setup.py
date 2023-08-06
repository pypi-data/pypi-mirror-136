# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['artificial_detection',
 'artificial_detection.data',
 'artificial_detection.models',
 'artificial_detection.models.smr']

package_data = \
{'': ['*']}

install_requires = \
['EasyNMT==2.0.1',
 'autoflake==1.4',
 'datasets==1.15.1',
 'dvc[gdrive]==2.9.3',
 'filelock==3.4.2',
 'huggingface==0.0.1',
 'numpy==1.21.4',
 'packaging==21.3',
 'pandas==1.3.4',
 'requests==2.27.1',
 'scikit-learn==1.0.1',
 'sklearn==0.0',
 'torch==1.10.1',
 'transformers==4.12.3',
 'wandb==0.12.6']

setup_kwargs = {
    'name': 'artificial-detection',
    'version': '0.1.0',
    'description': 'Python framework for artificial text detection with NLP approaches.',
    'long_description': None,
    'author': 'Marat Saidov',
    'author_email': 'msaidov1@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MaratSaidov/artificial-text-detection',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
