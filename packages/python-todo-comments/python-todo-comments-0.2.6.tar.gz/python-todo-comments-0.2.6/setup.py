# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_todo_comments']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['py-todos = python_todo_comments.main:main']}

setup_kwargs = {
    'name': 'python-todo-comments',
    'version': '0.2.6',
    'description': "A cli that will search for and parse TODO comments in a directory's python modules.",
    'long_description': "# Python # TODO:  \n\n\nThis project provides a cli that takes a directory as an argument, and returns the `# TODO:` comments from all the python modules under that directory.\n\nIt will output in a markdown-friendly way, and is meant as a repeatable way to keep on top of all of the little todos that are peppered throughout a project.\n\n\n## Installation\n\n`pip install python-todo-comments`\n\n\n\n## Usage\n\nThe basic command is `py-todos` combined with the following arguments:\n\n- No argument: will search and parse the current working directory\n- `-d` or `--dir` will search and parse the directory provided\n- `-o` or `--output` will write the output to the provided filename\n- `-h` or `--help` will provide the command's help context",
    'author': 'Tylor Dodge',
    'author_email': 'tdodge@nexamp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dodget/python-todo-comments',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
