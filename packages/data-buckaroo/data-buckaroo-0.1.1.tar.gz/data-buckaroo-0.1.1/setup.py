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
    'version': '0.1.1',
    'description': 'Description',
    'long_description': '# Data Buckaroo\n\nLightweight AWS Data Wrangler, for Athena queries only. Also has a lightweight "DataFrame" implementation if you prefer not to use Pandas.\n\n### Install\n\n```bash\npip install data-buckaroo\n# Optional if you would like to use Pandas\npip install data-buckaroo[pandas]\n```\n\n### Usage\n\n```python\nfrom data_buckaroo import AthenaQuery\nfrom lightframe import LightFrame\naq = AthenaQuery(workgroup="ATHENA_WORKGROUP", database="ATHENA_DATABASE")\nlf: LightFrame = aq.read_sql_query("SELECT * FROM TABLE_NAME")\nprint(lf)\n```\n```\n   id  string_object  string  float  int        date            timestamp   bool  par0  par1\n0   1            foo     foo    1.0    1  2020-01-01  2020-01-01 00:00:00   True     1     a\n1   2                                                                                1     b\n2   3            boo     boo    2.0    2  2020-01-02  2020-01-02 00:00:01  False     2     b\n```\n',
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
