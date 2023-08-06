# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ref_man_py']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'beautifulsoup4>=4.9.1,<5.0.0',
 'common_pyutil>=0.8.0,<0.9.0',
 'flask>=1.1.2,<2.0.0',
 'lxml>=4.6.4,<5.0.0',
 'psutil>=5.8.0,<6.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['ref_man = ref_man_py.__main__:main',
                     'test = pytest:main']}

setup_kwargs = {
    'name': 'ref-man-py',
    'version': '0.3.9',
    'description': 'Ref Man Python Module',
    'long_description': "* ref-man-py\n\n  Python Module for ~ref-man~ (See https://github.com/akshaybadola/ref-man).\n\n  Network requests and xml parsing can be annoying in emacs, so ref-man uses a\n  separate python process for efficient (and sometimes parallel) fetching of\n  network requests.\n\n* Features\n\n** HTTP integration with Semantic Scholar API (https://www.semanticscholar.org/product/api)\n   - Fetch with multiple IDs like arxiv, ACL etc.\n   - Local files based cache to avoid redundant requests\n   - Fetches all metadata in one go (Will change soon as Semantic Scholar is\n     updating its API)\n\n** Experimental (and undocumented) Semantic Scholar Search API\n   - Mostly gleaned through analyzing network requests. Helpful for searching\n     articles.\n\n** HTTP integration with DBLP and ArXiv\n   - Supports multiple parallel requests for batch updates\n\n** Fetch PDF from a given URL\n   - Easier to fetch using python than with Emacs's callbacks\n\n** Option for proxying requests\n   - Particularly useful for PDFs if you're tunneling to your institution from\n     home or some other location and the article you want is with institutional\n     (IP based) access only.\n\n",
    'author': 'Akshay',
    'author_email': 'akshay.badola.cs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/akshaybadola/ref-man-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
