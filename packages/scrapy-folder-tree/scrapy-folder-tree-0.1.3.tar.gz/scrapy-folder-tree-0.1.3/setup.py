# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['scrapy_folder_tree', 'scrapy_folder_tree.trees']

package_data = \
{'': ['*']}

install_requires = \
['Scrapy>=2.5.1,<3.0.0']

setup_kwargs = {
    'name': 'scrapy-folder-tree',
    'version': '0.1.3',
    'description': 'A scrapy pipeline which stores files using folder trees.',
    'long_description': "# scrapy-folder-tree\n\n [![build](https://github.com/sp1thas/scrapy-folder-tree/actions/workflows/build.yml/badge.svg)](https://github.com/sp1thas/scrapy-folder-tree/actions/workflows/build.yml) ![PyPI](https://img.shields.io/pypi/v/scrapy-folder-tree) [![GitHub license](https://img.shields.io/github/license/sp1thas/scrapy-folder-tree)](https://github.com/sp1thas/scrapy-folder-tree/blob/master/LICENSE) ![PyPI - Format](https://img.shields.io/pypi/format/scrapy-folder-tree) ![PyPI - Status](https://img.shields.io/pypi/status/scrapy-folder-tree) ![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg) ![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg) ![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)\n\nThis is a scrapy pipeline that provides an easy way to store files and images using various folder structures.\n\n\n## Supported folder structures:\n\nGiven this scraped file: `05b40af07cb3284506acbf395452e0e93bfc94c8.jpg`, you can choose the following folder structures:\n\n\n<details>\n  <summary>Using file name</summary>\n\n  class: `scrapy-folder-tree.ImagesHashTreePipeline`\n  \n  ```\n  full\n  ├── 0\n  .   ├── 5\n  .   .   ├── b\n  .   .   .   ├── 05b40af07cb3284506acbf395452e0e93bfc94c8.jpg\n  ```\n</details>\n\n\n<details>\n  <summary>Using crawling time</summary>\n\n  class: `scrapy-folder-tree.ImagesTimeTreePipeline`\n  \n  ```\n  full\n  ├── 0\n  .   ├── 11\n  .   .   ├── 48\n  .   .   .   ├── 05b40af07cb3284506acbf395452e0e93bfc94c8.jpg\n  ```\n</details>\n\n\n<details>\n  <summary>Using crawling date</summary>\n\n  class: `scrapy-folder-tree.ImagesDateTreePipeline`\n  \n  ```\n  full\n  ├── 2022\n  .   ├── 1\n  .   .   ├── 24\n  .   .   .   ├── 05b40af07cb3284506acbf395452e0e93bfc94c8.jpg\n  ```\n</details>\n\n\n## Installation\n\n```shell\npip install scrapy_folder_tree\n```\n\n## Usage\n\nUse the following settings in your project:\n```python\nITEM_PIPELINES = {\n    'scrapy_folder_tree.FilesHashTreePipeline': 300\n}\n\nFOLDER_TREE_DEPTH = 3\n```",
    'author': 'Panagiotis Simakis',
    'author_email': None,
    'maintainer': 'Panagiotis Simakis',
    'maintainer_email': None,
    'url': 'https://github.com/sp1thas/scrapy-folder-tree',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
