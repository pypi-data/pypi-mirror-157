# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['path_tree_generator', 'path_tree_generator.models']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'path-tree-generator',
    'version': '0.0.1',
    'description': 'Generate human-readable directory listings in a tree-like format as `list[str]`, `dict` or `json`',
    'long_description': '# path-tree-generator\n\nGenerate human-readable directory listings in a tree-like format as `list[str]`, `dict` or `json`\n\n    from path_tree_generator import PathTree\n    pt = PathTree(\'/my/path/to/generate\')\n    print(\n        pt.human_readable()\n    )\n\n----------------------------------------------------------------------------------------------------\n\n**ATTENTION: NOT FULLY IMPLEMENTED YET :construction:**\n\n:warning: CURRENTLY THIS PACKAGE IS UNDER HEAVY DEVELOPMENT AND NOT FULLY IMPLEMENTED YET! :warning:\n\nThe fist working (early) version is released as **path-tree-generator v0.0.1** \nand contains the most base implementations.\n\n[More to come for **path-tree-generator v0.1.0**:][issue-tracker]\n- Adding a "better" getter methods naming\n- Extend tests to check all possible parameters of a method or class\n- ...\n\nBut keep in mind that classes, methods and their signatures \nmight change anytime during development till the first official release 1.0.0.\n\n----------------------------------------------------------------------------------------------------\n\n## Table of Contents\n\n- [Requirements](#requirements)\n- [Usage](#usage)\n  - [Installation](#installation)\n  - [Example](#example)\n- [Support](#support)\n- [Contributing](#contributing)\n- [License](#license)\n- [Known Issues](#known-issues)\n\n## Requirements\n\n[Python 3.10][python]+\n\n`path-tree-generator` depends on the following packages:\n\n- [Pydantic][pydantic] for data models and validation\n\n## Usage\n\n### Installation\n\n    pip install path-tree-generator\n\n### Example\n\n    from path_tree_generator import PathTree\n    pt = PathTree(\'/my/path/to/generate\')\n    print(\n        pt.human_readable()\n    )\n\nThe code above outputs a tree-like formatted recursive directory listing.\nDirectories are wrapped in square brackets, files aren\'t.\n\n    [data]\n    ├── data.json\n    ├── data.tree\n    ├── [myDirectory-1]\n    │   ├── myFile.txt\n    │   └── [subdirectory]\n    │       └── green.gif\n    └── [myDirectory-2]\n        ├── [subdirectory1]\n        │   └── green.gif\n        └── [subdirectory2]\n            ├── myFile.txt\n            └── myFile2.txt\n\n## Support\n\nIf you\'re opening [issues][issue-tracker], please mention the version that the issue relates to. \n\n## Contributing\n\nTo contribute to this project, fork the repository, make your changes and create a pull request.\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n\n## Known Issues\n\n- Python version compatibility < v3.10 is not tested yet\n- Getter methods aren\'t named perfectly, this will be solved in a future version\n- Not all tests are fully implemented yet\n\n\n\n[issue-tracker]: https://github.com/dl6nm/path-tree-generator/issues\n[pydantic]: https://pydantic-docs.helpmanual.io/\n[python]: https://www.python.org/\n',
    'author': 'DL6NM',
    'author_email': 'mail@dl6nm.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dl6nm/path-tree-generator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
