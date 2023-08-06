# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src', 'api': 'src/api'}

packages = \
['api', 'core', 'core.action', 'core.loaders']

package_data = \
{'': ['*']}

install_requires = \
['networkx>=2.6.0,<3.0.0', 'setuptools>=33.1.0']

entry_points = \
{'kraken.core.loaders': ['pyscript = '
                         'kraken.core.loaders.pyscript:PyscriptLoader']}

setup_kwargs = {
    'name': 'kraken-core',
    'version': '0.1.1',
    'description': '',
    'long_description': '# kraken-core\n\nThe kraken core API provides the primitives to fully describe complex build processes of software components.\n\n## 1. Concepts\n\n### 1.1 Projects\n\nA project maps to a directory on the file system that represents a software component, usually\ncomprised of many different source code and supporting files, and eventually additional other\nsub projects.\n\nIn every build there is at least one project involved, the root project. When tasks are referenced\nby the full qualified name, the root project name is omitted from the path (similar to how the root\ndirectory in a file system does not have a name and is represented by a single slash).\n\n### 1.2 Tasks\n\nA task is a logical unit of work that has a unique name within the project it is associated with. Tasks\ncan have dependencies on other tasks or groups of tasks, even across projects. When a task is optional,\nit will only be executed if strictly required by another task.\n\nDependencies on task can be strict or non-strict. Non-strict dependencies enforce an order on the\nexecution sequence of tasks, wheras strict dependencies will ensure that the dependency has been\nexecuted.\n\nTasks are usually marked as "default", meaning that they are selected by default if no task selectors are\nspecified (see below on [Task selectors](#14-task-selectors)).\n\nEvery task is associated with one [Action](#15-actions) that is executed for the task.\n\n### 1.4 Task selectors\n\nWithout any arguments, all default tasks are selected and executed. When an explicit selection is made,\nit can be in one of the following forms:\n\n1. A fully qualified project reference\n2. A fully qualified task reference\n3. A task name to select from all projects that contain it\n\nProjects and tasks are structured hierarchally and fully qualified references are constructed like file system\npaths but with colons instead of slashes. For example, `:` represents the root roject, `:foo:bar` references\ntask or project `bar` in project `foo` in the root project, `spam` references all tasks named `spam`.\n\n### 1.5 Actions\n\nAn action is a unit of work that is executed by a task. A task\'s action may be set on creation or only right before\nit needs to be executed, in the `Task.finalize()` method.\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
