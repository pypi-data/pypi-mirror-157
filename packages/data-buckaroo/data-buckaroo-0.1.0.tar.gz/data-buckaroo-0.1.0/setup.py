# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src', 'lightframe': 'src/lightframe'}

packages = \
['data_buckaroo', 'lightframe']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'botocore', 'tabulate']

extras_require = \
{'pandas': ['pandas']}

setup_kwargs = {
    'name': 'data-buckaroo',
    'version': '0.1.0',
    'description': 'Description',
    'long_description': '# Data Buckaroo\n\nLightweight AWS Data Wrangler, for Athena queries only\n\n### Install\n\n```bash\npip install data-buck\n```',
    'author': 'Daniel Sullivan',
    'author_email': 'mumblepins@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mumblepins/data-buckaroo/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
