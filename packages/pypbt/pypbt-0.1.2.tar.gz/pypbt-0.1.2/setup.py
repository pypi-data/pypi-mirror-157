# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pypbt']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pypbt = pypbt.runner:main']}

setup_kwargs = {
    'name': 'pypbt',
    'version': '0.1.2',
    'description': 'Library of functions to write Property Based Tests in python',
    'long_description': '# pypbt\n\nThis library implements functions to write _property based tests_ in\npython.\n\nIt started as a proof of concept. By now there are still some missing\nfeatures:\n\n  - Shrinking\n  \n  - Generation strategies\n  \n  - State machines\n  \nWe can not make any promises about them.\n\n\n## Installation\n\n```\npip install pypbt\n```\n\n## Documentation\n\nSee [documentation on readthedocs](https://pypbt.readthedocs.io/en/latest/).\n\n## Support\n\nPlease [open an issue](https://github.com/cabrero/pypbt/issues) for support.\n\n## License\n\nThe project is licensed under the LGPL license.\n',
    'author': 'David Cabrero Souto',
    'author_email': 'david.cabrero@madsgroup.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cabrero/pypbt',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
