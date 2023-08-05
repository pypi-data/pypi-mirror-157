# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gobomatic', 'gobomatic.blocks']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'gobomatic',
    'version': '2.0.0',
    'description': 'Gobomatic is a Python library to generate Scratch (3>) projects from Object-Oriented representation of Scratch projects in Python code.',
    'long_description': '# Gobomatic\n\nGobomatic is a Python library to generate Scratch (3>) projects from\nObject-Oriented representation of Scratch projects in Python code.\n\n## Example\n\nA build.py file is used to build the Scratch project. It also defines the Stage\nsprite.\n\nbuild.py\n```py\nfrom gobomatic import *\n\nfrom main import Self as main\n\nstage = Sprite(\n    "Stage",\n    costumes = [\n        "assets/blank.svg"\n    ]\n)\n\nSelf = Project(\n    sprites = [\n        stage,\n        main\n    ]\n)\n\nSelf.export("project.sb3", debug=True)\n```\n\nEach sprite is defined in its own Python file.\n\nmain.py\n```py\nfrom gobomatic import *\n\nSelf = Sprite(\n    name=__name__,\n    costumes = [\n        "assets/scratchcat.svg"\n    ]\n)\n\nSelf.WhenFlagClicked(\n    Goto(-100, 0),\n    Glide(0, 0, 0.5),\n    Say("Hello, World!"),\n)\n```\n\n### Resulting project code\n![e](docs/assets/example-in-blocks.png)\n\n\n## Documentation\n[~/docs/docs.md](docs/docs.md)\n\n# Contributing\n\nYou can help with the development of gobomatic by testing or writing documentation.\n\n### Installation from source\n\nclone the repository (You should fork the repository first!)\n```\ncd ~/Projects\ngit clone https://github.com/aspizu/gobomatic gobomatic-git\n```\n\ninstall the module in edit mode\n```\ncd gobomatic-git\npip install -e .\n```\n\n### Testing\n\nUse [~/examples/testing](examples/testing) to test various Scratch code.\n\nbuilding the project\n```\ncd examples/testing\npython build.py\n```\n\nopen testing.sb3 in the Scratch editor to examine the result.\n',
    'author': 'aspizu',
    'author_email': 'aspizu@protonmail.com',
    'maintainer': 'aspizu',
    'maintainer_email': 'aspizu@protonmail.com',
    'url': 'https://github.com/aspizu/gobomatic',
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
