# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zeph', 'zeph.selectors', 'zeph_utils']

package_data = \
{'': ['*']}

install_requires = \
['diamond-miner>=0.7.1,<0.8.0',
 'mrtparse>=2.0.1,<3.0.0',
 'py-radix>=0.10.0,<0.11.0',
 'requests>=2.25.0,<3.0.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['zeph = zeph.__main__:run',
                     'zeph-bgp-convert = zeph_utils.zeph_bgp_convert:run',
                     'zeph-bgp-download = zeph_utils.zeph_bgp_download:run']}

setup_kwargs = {
    'name': 'dioptra-zeph',
    'version': '1.1.0',
    'description': 'An orchestrator for distributed IP tracing',
    'long_description': '# 🌬️ Zeph\n\n[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/zeph/Tests?logo=github)](https://github.com/dioptra-io/zeph/actions/workflows/tests.yml)\n[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/zeph?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/zeph)\n[![PyPI](https://img.shields.io/pypi/v/dioptra-zeph?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/dioptra-zeph/)\n\n> Zeph is a reinforcement learning based algorithm for selecting prefixes to probe based on previous measurements in order to maximize the number of nodes and links discovered. Zeph can be used on top of the [Iris](https://iris.dioptra.io) platform.\n\n\n## 🚀 Quickstart\n\nZeph has a command line interface to configure and run the algorithm.\n\nFirst, create the Python virtual environment:\n\n```\npoetry install \n```\n\nThen, execute `poetry run zeph`:\n\n```\nUsage: zeph.py [OPTIONS]\n\nOptions:\n  --api-url TEXT                  [default: https://api.iris.dioptra.io]\n  --api-username TEXT             [required]\n  --api-password TEXT             [required]\n  --database-url TEXT             [default:\n                                  http://localhost:8123?database=iris]\n\n  --bgp-prefixes-path PATH        [required]\n  --agent-tag TEXT                [default: all]\n  --tool TEXT                     [default: diamond-miner]\n  --protocol TEXT                 [default: icmp]\n  --min-ttl INTEGER               [default: 2]\n  --max-ttl INTEGER               [default: 32]\n  --epsilon FLOAT                 [default: 0.1]\n  --previous-measurement-uuid UUID\n  --fixed-budget INTEGER\n  --dry-run / --no-dry-run        [default: False]\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n\n  --help                          Show this message and exit.\n```\n\n## ✨ Generate the BGP prefix file \n\nZeph needs to know the set of BGP prefixes that it can probe. \nYou can create a BGP prefix file by downloading the latest RIB from [routeviews.org](http://routeviews.org) and then convert it into a pickle file.\n\nThe easiest way to do that is to use the command line tools located in the `utils/` folder.\n\n### Download the RIB\n\n`poetry run zeph-bgp-download`\n\n```\nUsage: zeph_bgp_download.py [OPTIONS]\n\nOptions:\n  --latestv4 / --no-latestv4      [default: False]\n  --latestv6 / --no-latestv6      [default: False]\n  --filepath PATH\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n\n  --help                          Show this message and exit.\n  ```\n\n### Convert the RIB to a pickle file\n\n`poetry run zeph-bgp-convert`\n\n```\nUsage: zeph_bgp_convert.py [OPTIONS] ROUTEVIEWS_FILEPATH\n\nArguments:\n  ROUTEVIEWS_FILEPATH  [required]\n\nOptions:\n  --bgp-prefixes-path PATH\n  --excluded-prefixes-path PATH\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n\n  --help                          Show this message and exit.\n```\n\n\n\n## 📚 Publications\n\n```\n```\n\n## 🧑\u200d💻 Authors\n\nIris is developed and maintained by the [Dioptra group](https://dioptra.io) at [Sorbonne Université](https://www.sorbonne-universite.fr) in Paris, France.\n',
    'author': 'Matthieu Gouel',
    'author_email': 'matthieu.gouel@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dioptra-io/zeph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
