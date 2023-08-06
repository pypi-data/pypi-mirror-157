# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['komposer', 'komposer.core', 'komposer.types']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'stringcase>=1.2.0,<2.0.0']

entry_points = \
{'console_scripts': ['komposer = komposer.cli:main']}

setup_kwargs = {
    'name': 'komposer',
    'version': '0.1.0.dev6',
    'description': 'Tool to convert a Docker Compose file into a Kubernetes manifest',
    'long_description': '# komposer\n\n## To-do\n\n- disallow port mapping form docker compose\n- set ingress annotations from CLI as file\n- set deployment annotations from CLI as file\n- accept repository and branch name only as kubernetes names\n- set ingress paths from CLI\n- needs the ingress class name, mandatory if ingress is selected\n- set custom resource limits\n',
    'author': 'Daniele Esposti',
    'author_email': 'daniele.esposti@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/expobrain/komposer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
