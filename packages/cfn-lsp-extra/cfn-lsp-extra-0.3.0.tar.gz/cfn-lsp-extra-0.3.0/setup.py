# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cfn_lsp_extra',
 'cfn_lsp_extra.completions',
 'cfn_lsp_extra.decode',
 'cfn_lsp_extra.resources',
 'cfn_lsp_extra.scrape']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aiohttp[speedups]>=3.8,<4.0',
 'cfn-lint>=0.59,<0.60',
 'click>=8.1.3,<9.0.0',
 'platformdirs==2.5',
 'pydantic==1.8',
 'pygls>=0.11,<0.12',
 'tqdm==4.64',
 'types-PyYAML>=6.0,<7.0']

entry_points = \
{'console_scripts': ['cfn-lsp-extra = cfn_lsp_extra.__main__:main']}

setup_kwargs = {
    'name': 'cfn-lsp-extra',
    'version': '0.3.0',
    'description': 'Cfn Lsp Extra',
    'long_description': "# Cfn Lsp Extra\n\n![Python Version](https://img.shields.io/pypi/pyversions/cfn-lsp-extra) [![Version](https://img.shields.io/github/v/tag/laurencewarne/cfn-lsp-extra?label=release)](CHANGELOG.md) [![codecov](https://codecov.io/gh/LaurenceWarne/cfn-lsp-extra/branch/master/graph/badge.svg?token=48ixiDIBpq)](https://codecov.io/gh/LaurenceWarne/cfn-lsp-extra)\n\nAn experimental cloudformation lsp server built on top of [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) aiming to provide hovering, completion, etc.  YAML and JSON are supported, though YAML has more features currently implemented (for example snippets) and will give a better experience.  Trust me.\n\nhttps://user-images.githubusercontent.com/17688577/176939586-df1d9ed8-5ec6-46d5-9f26-7222644047bd.mp4\n\n## Features\n\n| Method                            | Status                                                                                                          |\n|-----------------------------------|-----------------------------------------------------------------------------------------------------------------|\n| `textDocument/hover`              | Done for resources, resource properties, subproperties and `!Ref`s. *TODO* `!GetAtt`s, intrinsic functions. |\n| `textDocument/completion`         | Done for resources, resource properties, subproperties, refs and intrinsic functions. *TODO* `!GetAtt`.         |\n| `textDocument/definition`         | Done for `!Ref`s.  *TODO* mappings.                                                                             |\n| `textDocument/publishDiagnostics` | Done through `cfnlint`.                                                                                         |\n\n## Installation\n\nFirst install the executable, [`pipx`](https://pypa.github.io/pipx/) is recommended, but you can use `pip` instead if you like to live dangerously:\n\n```bash\npipx install cfn-lsp-extra\n```\n\nOr get the bleeding edge from source:\n\n```bash\npipx install git+https://github.com/laurencewarne/cfn-lsp-extra.git@$(git ls-remote git@github.com:laurencewarne/cfn-lsp-extra.git | head -1 | cut -f1)\n```\n\nUpdating:\n\n```bash\npipx upgrade cfn-lsp-extra\n```\n\n### Emacs\n\nInstall the [lsp-cfn.el](https://github.com/LaurenceWarne/lsp-cfn.el) package.\n\nPatches detailing integration steps for other editors are very welcome 🙏\n\n## Alternatives\n\n### [vscode-cfn-lint](https://github.com/aws-cloudformation/cfn-lint-visual-studio-code)\n\n### [cfn-lint](https://github.com/aws-cloudformation/cfn-lint)\n\nNote this is used by `cfn-lsp-extra` under the hood to generate [diagnostics](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic).  One difference with `cfn-lsp-extra` is that diagnostics will be refreshed every time you make a change to the document, in other words you don't need to save the file.\n",
    'author': 'Laurence Warne',
    'author_email': 'laurencewarne@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/laurencewarne/cfn-lsp-extra',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
