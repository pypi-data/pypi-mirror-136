# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['utubetomp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'utubetomp',
    'version': '0.1.0.1',
    'description': 'Converts a YouTube video to MP4 or MP3..',
    'long_description': '# utubetomp\n\nConverts a YouTube video to MP4 or MP3..\n\n## Installation\n\n```bash\n$ pip install utubetomp\n```\n\n## Usage\n\n- <a href="https://github.com/Russian-Dev/UTubeToMP">GitHub: UTubeToMP</a>\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`utubetomp` was created by Russian-Dev. Russian-Dev retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.\n\n## Credits\n\n`utubetomp` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Russian-Dev',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
