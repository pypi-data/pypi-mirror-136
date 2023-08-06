# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['random_data_gen', 'random_data_gen.features']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.1,<2.0.0', 'pandas>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'random-data-gen',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Random Data Generator\n\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n\n\nThis is a test package to generate random transactional data. \n\nWith this package you can create a table with transactional data containing:\n\n- consumer_id: ID identifing the customer that does the transaction;\n- created_at: Date of transaction;\n- payment_value: Monetary value of transaction.\n\nAll this fields are customizable.\n\n## How to use\n\nYou can start the use o RandomDataGen with this example code:\n\n``` python\nfrom random_data_gen.data_generator import DataGenerator\n\nTRGenerator = DataGenerator(\n    n_rows=1000,\n    n_ids=100,\n    mean_spend=100,\n    std_spend=10,\n    start_date="2020-01-01",\n    end_date="2021-01-01",\n)\n\ndf = TRGenerator()\n```\n\nIn this snippet we defined a table with 1000 rows, 100 unique users, a mean spend in transactions of 100 u.m. a standard deviation in transactional spend of 10u.m., the start date (2020-01-01) and the end date (2021-01-01).\n\nThe *df* returned is in the form:\n\n```\n| consumer_id | created_at                    | payment_value |\n|-------------|-------------------------------|---------------|\n| 234         | 2020-02-03 02:15:12.051981122 | 120.10        |\n| 43          | 2020-05-11 08:47:34.054054054 | 87.10         |\n| 3123        | 2020-12-30 21:37:17.837837840 | 12.84         |\n```',
    'author': 'Felipe Sassi',
    'author_email': 'felipe.sassi@datarisk.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
