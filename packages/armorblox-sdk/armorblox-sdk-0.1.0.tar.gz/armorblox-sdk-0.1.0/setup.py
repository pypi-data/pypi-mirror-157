# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['armorblox', 'armorblox.api']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5.2,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'armorblox-sdk',
    'version': '0.1.0',
    'description': 'Armorblox SDK for Python',
    'long_description': '<img src="https://assets.armorblox.com/f/52352/775x159/8fa6246e47/logo_color.svg" width=387 alt="Armorblox logo">\n\n# Armorblox Python SDK (Alpha)\n\n[![Apache-2 License](https://img.shields.io/badge/license-Apache2-blueviolet)](https://www.apache.org/licenses/LICENSE-2.0)\n\nThis is an alpha version of the SDK with limited documentation and no support.\n\n## Requirements\n\nPython 3.5+\n\n## Installation\n\n```\npip install armorblox-sdk\n```\n\n## Usage\n\n```\nfrom armorblox import client\n\n# Create an API client for your tenant\nc = client.Client(api_key=\'your-api-key-here\', instance_name=\'yourtenantname\')\n\n# Fetch a list of threats\nthreat_incidents = c.threats.list()\n\n# Fetch a specific threat\nincident = c.threats.get(44006)\n\n\n# Fetch a list of abuse incidents\nabuse_incidents = c.abuse_incidents.list()\n\n# Fetch a specific abuse incident\nabuse_incident = c.abuse_incidents.get(44200)\n\n\n# Fetch a list of DLP incidents\ndlp_incidents = c.dlp_incidents.list()\n\n# Fetch a specific DLP incident\ndlp_incident = c.dlp_incidents.get(44010)\n```\n\n## Contributing\n\n* Install [Poetry](https://python-poetry.org)\n* Clone the SDK repo & `cd` into it\n```\ngit clone https://github.com/armorblox/armorblox-python-sdk\ncd armorblox-python-sdk\n```\n* Run `poetry install` to install the dependencies\n* Run `tox` to run the tests\n\n## Publishing\n\n#### TestPyPI\n```\npoetry config repositories.test-pypi https://test.pypi.org/legacy/\npoetry config pypi-token.test-pypi <your-TestPyPI-token>\npoetry publish --build -r test-pypi\n```\n\nUse\n```\npip install --index-url https://test.pypi.org/simple/ --no-deps armorblox\n```\nto make sure the installation works correctly.\n\n#### PyPI\n```\npoetry config pypi-token.pypi <your-PyPI-token>\npoetry publish --build\n```\n',
    'author': 'Rajat Upadhyaya',
    'author_email': '45485+urajat@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/armorblox/armorblox-python-sdk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
