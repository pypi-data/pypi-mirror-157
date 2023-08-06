# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['turms',
 'turms.cli',
 'turms.parsers',
 'turms.plugins',
 'turms.processors',
 'turms.stylers']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.0',
 'graphql-core>=3.2.0,<4.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'rich>=11.0.0,<12.0.0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.9"': ['astunparse>=1.6.3,<2.0.0'],
 'black': ['black>=22.1.0,<23.0.0'],
 'isort': ['isort>=5.10.1,<6.0.0'],
 'watch': ['watchdog>=2.1.6,<3.0.0']}

entry_points = \
{'console_scripts': ['turms = turms.cli.main:entrypoint']}

setup_kwargs = {
    'name': 'turms',
    'version': '0.2.5a0',
    'description': 'graphql-codegen powered by pydantic',
    'long_description': '# turms\n\n[![codecov](https://codecov.io/gh/jhnnsrs/turms/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/turms)\n[![PyPI version](https://badge.fury.io/py/turms.svg)](https://pypi.org/project/turms/)\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/turms/)\n![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/turms.svg)](https://pypi.python.org/pypi/turms/)\n[![PyPI status](https://img.shields.io/pypi/status/turms.svg)](https://pypi.python.org/pypi/turms/)\n[![PyPI download month](https://img.shields.io/pypi/dm/turms.svg)](https://pypi.python.org/pypi/turms/)\n\n### BETA\n\n## Inspiration\n\nTurms is a pure python implementation following the awesome graphql-codegen library with a similar extensible design.\nIt makes heavy use of pydantic and its serialization capablities and provides fully typed querys, mutations and subscriptions\n\n## Supports\n\nSchema Generation\n- Enums\n- Inputs\n- Objects\n\nDocuments Generation\n- Fragments\n- Operations\n\n\n## Features\n\n- minimal, but fully documented code generation\n- agnostic of graphql transport (gql, and rath examples)\n- Autocollapsing operation functions\n- Specify type mixins, configuration\n- full support type hints for variables (Pylance)\n- Compliant with graphl-config\n- Support for custom scalars\n\n\n## Installation\n\n```bash\npip install turms\n```\n\n## Configuration\n\nTurms configuration is compliant with the graphql-config specification, allowing interoperability with other frameworks.\n\n```yaml\nprojects:\n  default:\n    schema: http://api.spacex.land/graphql/\n    documents: graphql/**.graphql\n    extensions:\n      turms: # path for configuration for turms\n        out_dir: examples/api\n        stylers:\n          - type: turms.stylers.capitalize.CapitalizeStyler\n          - type: turms.stylers.snake_case.SnakeCaseStyler\n        plugins:\n          - type: turms.plugins.enums.EnumsPlugin\n          - type: turms.plugins.inputs.InputsPlugin\n          - type: turms.plugins.fragments.FragmentsPlugin\n          - type: turms.plugins.operations.OperationsPlugin\n          - type: turms.plugins.funcs.FuncsPlugin\n        processors:\n          - type: turms.processors.black.BlackProcessor\n          - type: turms.processors.isort.IsortProcessor\n        scalar_definitions:\n          uuid: str\n          timestamptz: str\n          Date: str\n```\n\n## Run \n\n```bash\nturms gen\n```\n\n\nTurms configuration is based on plugins that can be configured in the graphql.config. There exist three major classes:\n\n### Stylers\n\nStylers are responsible for applying different styles to the class names and field names (e.g. snakecasing of graphqls pascalcase),\nthey are chained in order of notation in the graphql config (they receive the output of the last styler). Turms takes care of automatically\naliasing these names if they are not the same as the graphql style)\n\n### Plugins\n\nPlugins are the generators of code, that traverse through the direcotry and ad new ast nodes to the global tree. Examplary pluings are:\n\n- turms.plugins.enums.EnumsPlugin\n- turms.plugins.inputs.InputsPlugin\n- turms.plugins.fragments.FragmentsPlugin\n- turms.plugins.operations.OperationsPlugin\n- turms.plugins.funcs.FuncsPlugin\n\n## Parsers\n\nParsers take the generated python.AST, and can parse this code. (e.g enabling polyfills for different python versions)\nIncludes Parsers are\n\n- turms.parsers.polyfill.PolyfillParser (only working for python 3.7)\n\n## Processors\n\nProcessors take the generated code (already a string), and can parse this code. (e.g. black processor for enforcing black style formatting) or isort of sorting imports.\nIncludes Processors are\n\n- turms.processor.black.BlackProcessor\n- turms.processor.isort.IsortProcessor\n\n## Usage\n\nOpen your workspace (create a virtual env), in the root folder\n\n```bash\nturms init\n```\n\nThis creates a graphql-config compliant configuration file in the working directory, edit this to reflect your settings (see Configuration)\n\n```bash\nturms gen\n```\n\nGenerate beautifully typed Operations, Enums,...\n\n### Why Turms\n\nIn Etruscan religion, Turms (usually written as 𐌕𐌖𐌓𐌌𐌑 Turmś in the Etruscan alphabet) was the equivalent of Roman Mercury and Greek Hermes, both gods of trade and the **messenger** god between people and gods.\n\n## Transport Layer\n\nTurms does *not* come with a default transport layer but if you are searching for an Apollo-like GraphQL Client you can check out [rath](https://github.com/jhnnsrs/rath), that works especially well with turms.\n\n## Examples\n\nThis github repository also contains an example graphql.config.yaml with the public SpaceX api, as well as a sample of the generated api.\n\n## Experimental\n\n```bash\nturms watch $PROJECT_NAME\n```\n\nTurms watch is able to automatically monitor your graphql folder for changes and autogenerate the api on save again.\nRequires additional dependency for watchdog\n\n```bash\npip install turms[watch]\n```\n',
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
