# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot', 'nonebot.adapters.onebot_qq_extension']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.1.0,<3.0.0', 'nonebot2>=2.0.0b3,<3.0.0']

setup_kwargs = {
    'name': 'onebot-qq-extension',
    'version': '0.1.0',
    'description': '基于 OneBot v12 子协议 OneBot QQ Extension 实现的 nonebot2 适配器',
    'long_description': '<div align="center">\n\n# NoneBot-Adapter-OneBot-QQ-Extension\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_✨ OneBot 协议适配 ✨_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/nonebot/adapter-onebot/master/LICENSE">\n    <img src="https://img.shields.io/github/license/nonebot/adapter-onebot" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/onebot_qq_extension">\n    <img src="https://img.shields.io/pypi/v/onebot_qq_extension" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue" alt="python">\n  <a href="https://codecov.io/gh/nonebot/adapter-onebot">\n    <img src="https://codecov.io/gh/nonebot/adapter-onebot/branch/master/graph/badge.svg?token=45OH1IVM9C"/>\n  </a>\n  <a href="https://github.com/Sclock/onebot-qq-extensionactions/workflows/website-deploy.yml">\n    <img src="https://github.com/Sclock/onebot-qq-extension/actions/workflows/website-deploy.yml/badge.svg?branch=master&event=push" alt="site"/>\n  </a>\n  <br />\n  <a href="https://onebot.dev/">\n    <img src="https://img.shields.io/badge/OneBot-v12-black?style=social&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="cqhttp">\n  </a>\n  <br />\n  <a href="https://jq.qq.com/?_wv=1027&k=5OFifDh">\n    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-768887710-orange?style=flat-square" alt="QQ Chat Group">\n  </a>\n  <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=7b4a3&appChannel=share&businessType=9&from=246610&biz=ka">\n    <img src="https://img.shields.io/badge/QQ%E9%A2%91%E9%81%93-NoneBot-5492ff?style=flat-square" alt="QQ Channel">\n  </a>\n  <a href="https://t.me/botuniverse">\n    <img src="https://img.shields.io/badge/telegram-botuniverse-blue?style=flat-square" alt="Telegram Channel">\n  </a>\n  <a href="https://discord.gg/VKtE6Gdc4h">\n    <img src="https://discordapp.com/api/guilds/847819937858584596/widget.png?style=shield" alt="Discord Server">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://sclock.github.io/onebot-qq-extension/">文档</a>\n  ·\n  <a href="https://sclock.github.io/onebot-qq-extension/">安装</a>\n  ·\n  <a href="https://sclock.github.io/onebot-qq-extension/">开始使用</a>\n</p>\n\n# 安装\n\n```shell\npip install onebot_qq_extension\n```\n\n# 使用\n\n```python\nfrom nonebot.adapters.onebot_qq_extension import *\n```\n',
    'author': 'Sclock',
    'author_email': '1342810270@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sclock.github.io/onebot-qq-extension/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
