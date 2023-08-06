# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbtc', 'dbtc.client', 'dbtc.client.cloud', 'dbtc.client.metadata']

package_data = \
{'': ['*'], 'dbtc.client.metadata': ['artifacts/*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'sgqlc>=15.0,<16.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['dbtc = dbtc.cli:main']}

setup_kwargs = {
    'name': 'dbtc',
    'version': '0.1.2',
    'description': 'An unaffiliated python wrapper for dbt Cloud APIs',
    'long_description': '<p align="center">\n    <a href="#"><img src="img/dbt.png"></a>\n</p>\n<p align="center">\n    <em>An unaffiliated python interface for dbt Cloud APIs</em>\n</p>\n<p align="center">\n    <a href="https://codecov.io/gh/dpguthrie/dbtc" target="_blank">\n        <img src="https://img.shields.io/codecov/c/github/dpguthrie/dbtc" alt="Coverage">\n    </a>\n    <a href="https://pypi.org/project/dbtc" target="_blank">\n        <img src="https://badge.fury.io/py/dbtc.svg" alt="Package version">\n    </a>\n    <a href="https://pepy.tech/project/dbtc" target="_blank">\n        <img src="https://pepy.tech/badge/dbtc" alt="Downloads">\n    </a>\n</p>\n\n---\n\n**Documentation**: <a target="_blank" href="https://dbtc.dpguthrie.com">https://dbtc.dpguthrie.com</a>\n\n**Source Code**: <a target="_blank" href="https://github.com/dpguthrie/dbtc">https://github.com/dpguthrie/dbtc</a>\n\n**V2 Docs**: <a target="_blank" href="https://docs.getdbt.com/dbt-cloud/api-v2">https://docs.getdbt.com/dbt-cloud/api-v2</a>\n\n**V3 Docs (Unofficial)**: <a target="_blank" href="https://documenter.getpostman.com/view/14183654/UVsSNiXC">https://documenter.getpostman.com/view/14183654/UVsSNiXC</a>\n\n**V4 Docs**: <a target="_blank" href="https://docs.getdbt.com/dbt-cloud/api-v4">https://docs.getdbt.com/dbt-cloud/api-v4</a>\n\n---\n\n## Overview\n\ndbtc is an unaffiliated python interface to various dbt Cloud API endpoints.\n\nThis library acts as a convenient interface to two different APIs that dbt Cloud offers:\n\n- Cloud API:  This is a REST API that exposes endpoints that allow users to programatically create, read, update, and delete\nresources within their dbt Cloud Account.\n- Metadata API:  This is a GraphQL API that exposes metadata generated from a job run within dbt Cloud.\n\n## Requirements\n\nPython 3.7+\n\n- [Requests](https://requests.readthedocs.io/en/master/) - The elegant and simple HTTP library for Python, built for human beings.\n- [sgqlc]() - Simple GraphQL Client\n- [Typer](https://github.com/ross/requests-futures) - Library for building CLI applications\n\n## Installation\n\n```bash\npip install dbtc\n```\n## Basic Usage\n\n### Python\n\nThe interface to both APIs are located in the `dbtCloudClient` class.\n\nThe example below shows how you use the `cloud` property on an instance of the `dbtCloudClient` class to access methods that allow for programmatic control over dbt Cloud resources.\n\n```python\nfrom dbtc import dbtCloudClient\n\nclient = dbtCloudClient()\n\naccount = client.cloud.get_account_by_name(\'My Account\')\nproject = client.cloud.get_project_by_name(account[\'id\'], \'My Project\')\n\nrun_id = client.cloud.trigger_job_and_poll()\n```\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    'author': 'Doug Guthrie',
    'author_email': 'douglas.p.guthrie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
