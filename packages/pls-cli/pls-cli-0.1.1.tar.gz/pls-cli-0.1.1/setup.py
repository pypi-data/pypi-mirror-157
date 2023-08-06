# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pls_cli', 'pls_cli.utils']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.4.4,<13.0.0', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['pls = pls_cli.please:app']}

setup_kwargs = {
    'name': 'pls-cli',
    'version': '0.1.1',
    'description': '',
    'long_description': '<h1 align="center">\n  💻 PLS-CLI\n</h1>\n<p align="center">\n    <a href="https://github.com/guedesfelipe/pls-cli/actions/workflows/ci.yml" target="_blank">\n        <img src="https://github.com/guedesfelipe/pls-cli/actions/workflows/ci.yml/badge.svg?branch=main" />\n    </a>\n    <a href="https://github.com/guedesfelipe/pls-cli/actions/workflows/security.yml" target="_blank">\n        <img src="https://github.com/guedesfelipe/pls-cli/actions/workflows/security.yml/badge.svg?branch=main" />\n    </a>\n    <a href="https://codecov.io/gh/guedesfelipe/pls-cli" > \n      <img src="https://codecov.io/gh/guedesfelipe/pls-cli/branch/main/graph/badge.svg"/> \n    </a>\n    <a href="https://pypi.org/project/pls-cli/" target="_blank">\n      <img src="https://img.shields.io/pypi/v/pls-cli?label=pypi%20package" />\n    </a>\n    <a href="" target="_blank">\n      <img src="https://img.shields.io/pypi/pyversions/pls-cli.svg?color=green&logo=python&logoColor=yellow" />\n    </a>\n    <img src="https://img.shields.io/badge/platforms-windows%7C%20linux%7C%20macos-lightgrey" />\n</p>\n\n<p align="center">\n  <em>If you are like me, and your terminal is your home, this CLI will make your life better, I hope 😄</em>\n  <br>\n  <br>\n  <img src="https://user-images.githubusercontent.com/25853920/175831710-20fa013d-5b83-4fe0-baf9-f035345c9192.gif" />\n</p>\n\n# 🛠 Installation\n\n```sh\npip install pls-cli\n```\n\n# ⚙️ Configuration\n\nTo run **`pls-cli`** everytime you open your shell\'s:\n\n<details><p><summary>Bash</p></summary>\n\n```sh\necho \'pls\' >> ~/.bashrc\n```\n\n</details>\n\n<details><p><summary>Zsh</p></summary>\n\n```sh\necho \'pls\' >> ~/.zshrc\n```\n\n</details>\n\n<details><p><summary>Fish</p></summary>\n\n```sh\necho \'pls\' >> ~/.config/fish/config.fish\n```\n\n</details>\n\n<details><p><summary>Ion</p></summary>\n  \n```sh\necho \'pls\' >> ~/.config/ion/initrc\n```\n\n</details>\n\n<details><p><summary>Tcsh</p></summary>\n  \n```sh\necho \'pls\' >> ~/.tcshrc\n```\n\n</details>\n\n<details><p><summary>Xonsh</p></summary>\n\n```sh\necho \'pls\' >> ~/.xonshrc\n```\n</details>\n\n<details><p><summary>Powershell</p></summary>\n    \nAdd the following to the end of `Microsoft.PowerShell_profile.ps1`. You can check the location of this file by querying the `$PROFILE` variable in PowerShell. Typically the path is `~\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1` or `~/.config/powershell/Microsoft.PowerShell_profile.ps1` on -Nix.\n \n```txt\npls\n```\n\n</details>\n\n# ⌨️ Commands\n\n```sh\npls --help\n```\n\n```\n  add           Add a Task (Add task name inside quotes)\n  clean         Clean up tasks marked as done\n  clear         Clear all tasks\n  count-done    Count done tasks\n  count-undone  Count undone tasks\n  delete        Delete a Task\n  done          Mark a task as done\n  move          Change task order\n  setup         Reset all data and run setup\n  showtasks     Show all Tasks\n  undone        Mark a task as undone\n  version       Show version\n```\n\n\n# 🎨 Color Configuration\n\nYou can configure all colors with envs!!\n\n<details><p><summary>Setting env on Linux, macOS, Windows Bash:</p></summary>\n\n```sh\nexport PLS_ERROR_LINE_STYLE="#e56767"\n```\n\n</details>\n\n<details><p><summary>Setting env on Windows PowerShell:</p></summary>\n\n```sh\n$Env:PLS_ERROR_LINE_STYLE = "#e56767"\n```\n\n</details>\n\nAll envs:\n```sh\nexport PLS_ERROR_LINE_STYLE="#e56767"\nexport PLS_ERROR_TEXT_STYLE="#ff0000 bold"\n\nexport PLS_WARNING_LINE_STYLE="#FFBF00"\nexport PLS_WARNING_TEXT_STYLE="#FFBF00 bold"\n\nexport PLS_UPDATE_LINE_STYLE="#61E294"\nexport PLS_UPDATE_TEXT_STYLE="#61E294 bold"\n\nexport PLS_INSERT_DELETE_LINE_STYLE="#bb93f2"\n\nexport PLS_INSERT_DELETE_TEXT_STYLE="#a0a0a0"\n\nexport PLS_MSG_PENDING_STYLE="#61E294"\nexport PLS_TABLE_HEADER_STYLE="#844191"\nexport PLS_TABLE_HEADER_STYLE="#d77dd8"\nexport PLS_TASK_DONE_STYLE="#a0a0a0"\nexport PLS_TASK_PENDING_STYLE="#bb93f2"\nexport PLS_HEADER_GREETINGS_STYLE="#FFBF00"\nexport PLS_QUOTE_STYLE="#a0a0a0"\nexport PLS_AUTHOR_STYLE="#a0a0a0"\n```\n\n<details><p><summary>You can specify the background color like this:</p></summary>\n\n```sh\nexport PLS_QUOTE_STYLE="#a0a0a0 on blue"\n```\n\n</details>\n\nIf you create some theme, share with us <a href="https://github.com/guedesfelipe/pls-cli/discussions/1#discussion-4174647" target="_blank">here</a> ♥️.\n\n## 💄 Formatting a task\n\n<details><p><summary>You can format your tasks with:</p></summary>\n\n```sh\npls add "[b]Bold[/], [i]Italic[/], [s]Strikethrough[/], [d]Dim[/], [r]Reverse[/], [red]Color Red[/], [#FFBF00 on green]Color exa with background[/], :star:, ✨"\n```\n\n![image](https://user-images.githubusercontent.com/25853920/175835339-8059bc7e-0538-4e2d-aed8-80487d7b2478.png)\n\n</details>\n\n## 🚧 TMUX integration\n\nUsing `pls count-done` and `pls count-undone`.\n\n---\n\n<p align="center">\n  <a href="https://ko-fi.com/guedesfelipe" target="_blank">\n    <img src="https://user-images.githubusercontent.com/25853920/175832199-6c75d866-31b8-4209-bd1a-db116a6dd032.png" width=300 />\n  </a>\n</p>\n',
    'author': 'Felipe Guedes',
    'author_email': 'contatofelipeguedes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://guedesfelipe.github.io/pls-cli/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
