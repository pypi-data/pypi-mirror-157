# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src',
 'core': 'src/core',
 'core.loader': 'src/core/loader',
 'testing': 'src/testing'}

packages = \
['api', 'core', 'core.loader', 'testing']

package_data = \
{'': ['*']}

install_requires = \
['networkx>=2.6.0,<3.0.0', 'setuptools>=33.1.0', 'typeapi>=0.2.1,<0.3.0']

extras_require = \
{'testing': ['pytest>=6.0.0']}

entry_points = \
{'kraken.core.loader': ['pyscript = '
                        'kraken.core.loader.pyscript:PyscriptLoader']}

setup_kwargs = {
    'name': 'kraken-core',
    'version': '0.2.0',
    'description': '',
    'long_description': '# kraken-core\n\nThe `kraken.core` package provides the primitives of describing a build and deriving build tasks.\n\nAside from the `kraken.core` package, this package also provides the `kraken.api` module that is\nused only at runtime by Kraken build scripts and the `kraken.testing` module for Pytest fixtures.\n\n## How does it work?\n\nKraken uses **tasks** to describe units of work that can be chained and establish dependencies between each other.\nEach task has a **schema** that defines its input and output properties. When an output property is linked to the\ninput property of another task, this established as dependency between the tasks.\n\n```py\nfrom kraken.std.docker_gen import generate_dockerfile\nfrom kraken.std.docker_build import build_docker_image\ndockerfile = generate_dockerfile(source_file="Dockerfile.yml")\nbuild_docker_image(dockerfile=dockerfile.path, tags=["example:latest"], load=True)\n```\n\nThis populates the project with two **tasks** and connects the computed output property of one to the other,\nallowing the tasks that will run for `build_docker_image()` to pick up the dynamically generated Dockerfile that\nis written into a location in the build directory by the `generate_dockerfile()` task.\n\n<p align="center"><img src="assets/graph.png" height="225px"></p>\n\n## Core API\n\nKraken **tasks** are described with a schema. Each schema field has a type and may be an input or output parameter.\nOutput parameters are only available once a resource is executed; Kraken will that a proper execution order is\nestablished such that output properties are hydrated before another resource tries to access them as an input.\n\n```py\nfrom kraken.core.task import Context, Task, Property, Output, task_factory\nfrom typing_extensions import Annotated\n\nclass GenerateDockerfileTask(Task):\n    source_file: Property[str]\n    path: Annotated[Property[str], Output]\n\n    def execute(self, ctx: Context) -> None:\n        path = Path(self.path.setdefault(str(ctx.build_directory / "Dockerfile")))\n        path.write_text(render_dockerfile(Path(self.source_file.get()).read_text()))\n\ngenerate_dockerfile = task_factory(GenerateDockerfileTask)\n```\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
