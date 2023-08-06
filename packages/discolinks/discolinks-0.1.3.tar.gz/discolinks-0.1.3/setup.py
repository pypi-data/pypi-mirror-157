# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['discolinks']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.4.0,<22.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'click>=8.1.3,<9.0.0',
 'httpx>=0.23.0,<0.24.0',
 'rich>=12.4.4,<13.0.0']

entry_points = \
{'console_scripts': ['discolinks = discolinks.cli:main']}

setup_kwargs = {
    'name': 'discolinks',
    'version': '0.1.3',
    'description': 'Command-line tool which checks a website for broken links.',
    'long_description': "# discolinks\n\n[![Build Status][build_status_badge]][build_status_link]\n\nDiscolinks looks for broken links on a website.\n\nFeatures:\n\n- Starts on one page and recursively finds the other reachable pages on the website.\n- Asynchronous: Maximum number of parallel requests is configurable.\n- JSON output available: Useful for testing and scripting.\n\n## Getting Started\n\n```bash\n$ discolinks --url https://example.net\n📂 Results: 13 links (10 ok, 3 failed)\n├── 📄 https://example.net/foo\n│   ├── 🔗 /bad_absolute_href: 302 → 404\n│   └── 🔗 bad_relative_href: 404\n└── 📄 https://example.net/bar\n    └── 🔗 https://example.org/bad_external_href: Connection error\n```\n\n## Development\n\n```bash\n... # Activate virtualenv.\npoetry install\nmake check\n```\n\n## Release\n\n- Create a branch with a name like `release-1.2.3`.\n- Update version in `src/discolinks/__version__.py`.\n- Update version in `pyproject.toml`.\n- Update changelog.\n- Open a pull request and get it merged.\n- Tag the release `git tag --message 'Version 1.2.3' 1.2.3`\n- Push tags: `git push --tags`\n\n[build_status_badge]: https://github.com/bbc2/discolinks/actions/workflows/main.yml/badge.svg\n[build_status_link]: https://github.com/bbc2/discolinks/actions/workflows/main.yml\n",
    'author': 'Bertrand Bonnefoy-Claudet',
    'author_email': 'bertrand@bertrandbc.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
