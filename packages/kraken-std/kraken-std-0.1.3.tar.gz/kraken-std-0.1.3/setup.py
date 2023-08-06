# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['std', 'std.docker', 'std.generic', 'std.helm']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'kraken-core>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'kraken-std',
    'version': '0.1.3',
    'description': 'The Kraken standard library.',
    'long_description': '# kraken-std\n\nThe Kraken standard library.\n\n__Features__\n\n* [Docker](#docker)\n\n---\n\n## Docker\n\n  [Kaniko]: https://github.com/GoogleContainerTools/kaniko\n  [Buildx]: https://docs.docker.com/buildx/working-with-buildx/\n\nBuild and publish Docker images.\n\n__Supported backends__\n\n* [ ] Native Docker\n* [ ] [Buildx][]\n* [x] [Kaniko][]\n\n__Quickstart__\n\n```py\nfrom kraken.std import docker\n\ndocker.build(\n    name="buildDocker",\n    dockerfile=dockerfile.action.file,\n    dependencies=[dockerfile],\n    tags=["kraken-example"],\n    load=True,\n)\n```\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
