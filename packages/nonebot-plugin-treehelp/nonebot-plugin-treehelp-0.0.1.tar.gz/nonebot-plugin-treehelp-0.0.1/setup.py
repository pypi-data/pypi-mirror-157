# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_treehelp']

package_data = \
{'': ['*']}

install_requires = \
['nonebot2>=2.0.0-beta.4,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-treehelp',
    'version': '0.0.1',
    'description': '适用于 Nonebot2 的树形帮助插件',
    'long_description': '<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBot Plugin TreeHelp\n\n_✨ NoneBot 树形帮助插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-treehelp/main/LICENSE">\n    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-treehelp.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-treehelp">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-treehelp.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue.svg" alt="python">\n  <a href="https://codecov.io/gh/he0119/nonebot-plugin-treehelp">\n    <img src="https://codecov.io/gh/he0119/nonebot-plugin-treehelp/branch/main/graph/badge.svg?token=jd5ufc1alv"/>\n  </a>\n</p>\n\n## 使用方式\n\n加载插件后发送 `/help` 获取具体用法。\n\n## 配置项\n\n配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。\n',
    'author': 'hemengyang',
    'author_email': 'hmy0119@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/he0119/nonebot-plugin-treehelp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
