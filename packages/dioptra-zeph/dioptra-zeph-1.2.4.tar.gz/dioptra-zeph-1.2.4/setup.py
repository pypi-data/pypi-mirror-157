# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zeph', 'zeph.rankers', 'zeph.selectors', 'zeph_utils']

package_data = \
{'': ['*']}

install_requires = \
['diamond-miner>=1.0.0,<2.0.0',
 'dioptra-iris-client>=0.4.5,<0.5.0',
 'py-radix>=0.10.0,<0.11.0',
 'pyasn>=1.6.1,<2.0.0',
 'pych-client[orjson]>=0.3.0,<0.4.0',
 'requests>=2.25.0,<3.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['zeph = zeph.main:app',
                     'zeph-bgp-convert = zeph_utils.zeph_bgp_convert:run']}

setup_kwargs = {
    'name': 'dioptra-zeph',
    'version': '1.2.4',
    'description': 'An orchestrator for distributed IP tracing',
    'long_description': '# 🌬️ Zeph\n\n[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/zeph/Tests?logo=github)](https://github.com/dioptra-io/zeph/actions/workflows/tests.yml)\n[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/zeph?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/zeph)\n[![PyPI](https://img.shields.io/pypi/v/dioptra-zeph?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/dioptra-zeph/)\n\n> Zeph is a reinforcement learning based algorithm for selecting prefixes to probe based on previous measurements in order to maximize the number of nodes and links discovered. Zeph can be used on top of the [Iris](https://iris.dioptra.io) platform.\n\n\n## 🚀 Quickstart\n\nZeph has a command line interface to configure and run the algorithm.\n\nFirst, install the Zeph package:\n\n```\npip install dioptra-zeph\n```\n\nZeph takes as input a list of /24 (IPv4) or /64 (IPv6) prefixes:\n```sh\n# prefixes.txt\n8.8.8.0/24\n2001:4860:4860::/64\n```\n\nTo start a measurement from scratch:\n```bash\nzeph prefixes.txt\n```\n\nTo start from a previous measurement:\n```bash\nzeph prefixes.txt UUID\n```\n\nZeph relies on [iris-client](https://github.com/dioptra-io/iris-client) and [pych-client](https://github.com/dioptra-io/pych-client)\nfor communicating with Iris and ClickHouse. See their respective documentation to know how to specify the credentials.\n\n## ✨ Generate prefix lists from BGP RIBs\n\nYou can create an _exhaustive_ list of /24 prefixes from a BGP RIB dump:\n```bash\npyasn_util_download.py --latest\n# Connecting to ftp://archive.routeviews.org\n# Finding most recent archive in /bgpdata/2022.05/RIBS ...\n# Downloading ftp://archive.routeviews.org//bgpdata/2022.05/RIBS/rib.20220524.1000.bz2\n#  100%, 659KB/s\n# Download complete.\nzeph-bgp-convert --print-progress rib.20220524.1000.bz2 prefixes.txt\n```\n\n## 📚 Publications\n\n```bibtex\n@article{10.1145/3523230.3523232,\n    author = {Gouel, Matthieu and Vermeulen, Kevin and Mouchet, Maxime and Rohrer, Justin P. and Fourmaux, Olivier and Friedman, Timur},\n    title = {Zeph &amp; Iris Map the Internet: A Resilient Reinforcement Learning Approach to Distributed IP Route Tracing},\n    year = {2022},\n    issue_date = {January 2022},\n    publisher = {Association for Computing Machinery},\n    address = {New York, NY, USA},\n    volume = {52},\n    number = {1},\n    issn = {0146-4833},\n    url = {https://doi.org/10.1145/3523230.3523232},\n    doi = {10.1145/3523230.3523232},\n    journal = {SIGCOMM Comput. Commun. Rev.},\n    month = {mar},\n    pages = {2–9},\n    numpages = {8},\n    keywords = {active internet measurements, internet topology}\n}\n```\n\n## 🧑\u200d💻 Authors\n\nIris is developed and maintained by the [Dioptra group](https://dioptra.io) at [Sorbonne Université](https://www.sorbonne-universite.fr) in Paris, France.\n',
    'author': 'Matthieu Gouel',
    'author_email': 'matthieu.gouel@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dioptra-io/zeph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
