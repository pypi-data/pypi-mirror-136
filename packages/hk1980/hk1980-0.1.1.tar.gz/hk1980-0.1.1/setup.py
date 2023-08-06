# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hk1980']

package_data = \
{'': ['*']}

install_requires = \
['pyproj>=3.3.0,<4.0.0']

setup_kwargs = {
    'name': 'hk1980',
    'version': '0.1.1',
    'description': 'A forked project from hk80. This project also convert the coordincates with pyproj, with a more update version and providing better performance',
    'long_description': '# hk1980\nGrid coordinates conversion library in Python between Hong Kong 1980 Grid System and World Geodetic System 1984\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) or [poetry](https://python-poetry.org/) to install foobar.\n\n```bash\npip install hk1980\n```\nor\n```bash\npoetry add hk1980\n```\n\n## Usage\n\n```python\nfrom hk1980 import LatLon, HK80\n\nhku = LatLon(22.284034, 114.137814).to_hk80()\nprint(hku.northing, hku.easting) # 836303.204 818195.94\nprint(hku.x, hku.y) # 818195.94 836303.204\n\nhku = HK80(northing=816128, easting=832243).to_wgs84()\nprint(hku.latitude, hku.longitude) # 22.42944514 113.98124272\nprint(hku.x, hku.y) # 113.98124272 22.42944514\n```\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'Kavan Chan',
    'author_email': 'kavandevelopment@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kavandev/hk1980',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
