# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloudlab_client']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=4.1.3,<5.0.0']

setup_kwargs = {
    'name': 'cloudlab-client',
    'version': '0.1.44',
    'description': 'Client for the cloudlab academic cloud environment.',
    'long_description': '# Cloudlab Client\n\nThis package is a client for the Cloudlab service. Cloudlab is a cloud for\nacademic institutions. Because I could not (yet) find any working API for\nCloudlab, the current client relies on username / password authentication and\nweb scraping.\n\n\n## Usage\n\n\n```python\n# Create new client and login\nusername = os.environ.get("CLOUDLAB_USERNAME")\npassword = os.environ.get("CLOUDLAB_PASSWORD")\ncloudlab_client = CloudlabClient()\ncloudlab_client.login(username, password)\n\n# List experiments\nexperiments = cloudlab_client.experiment_list()\nprint(experiments)\n\n# List an experiment\'s nodes\nnodes = cloudlab_client.experiment_list_nodes("my-experiment")\nprint(nodes)\n\n# Request an extension (e.g., for 6 days). Reason must be at least 120 characters.\nreason = ("Important experiment needed for research, conducted under advisor"\n          " <fill_your_advisor>. Particular machines are needed because"\n          " <fill_your_reasons>.")\ncloudlab_client.experiment_extend("my-experiment", reason, hours=6*24)\n```\n',
    'author': 'Yannis Zarkadas',
    'author_email': 'yanniszark@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
