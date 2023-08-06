# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_wordcloud']

package_data = \
{'': ['*']}

install_requires = \
['jieba>=0.42.1,<0.43.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-datastore>=0.2.0,<0.3.0',
 'nonebot2[httpx]>=2.0.0-beta.1,<3.0.0',
 'typing-extensions>=4.0.1,<5.0.0',
 'tzdata>=2021.5,<2022.0',
 'wordcloud>=1.8.1,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['numpy>=1.21.1,<2.0.0'],
 ':python_version <= "3.8"': ['backports.zoneinfo>=0.2.1,<0.3.0'],
 ':python_version >= "3.8"': ['numpy>=1.22.1,<2.0.0']}

setup_kwargs = {
    'name': 'nonebot-plugin-wordcloud',
    'version': '0.0.4',
    'description': '适用于 NoneBot2 的词云插件',
    'long_description': '<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBot Plugin WordCloud\n\n_✨ NoneBot 词云插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-wordcloud/master/LICENSE">\n    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-wordcloud.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-wordcloud">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-wordcloud.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue.svg" alt="python">\n</p>\n\n## 使用方式\n\n因为插件依赖数据库，所以需要在配置文件中添加\n\n```env\nDATASTORE_ENABLE_DATABASE=true\n```\n\n插件启动完成后，发送 `/今日词云` 或 `/昨日词云` 获取词云。\n\n## 配置项\n\n配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。\n\n### wordcloud_width\n\n- 类型: `int`\n- 默认: `1920`\n- 说明: 生成图片的宽度\n\n### wordcloud_height\n\n- 类型: `int`\n- 默认: `1200`\n- 说明: 生成图片的高度\n\n### wordcloud_background_color\n\n- 类型: `str`\n- 默认: `black`\n- 说明: 生成图片的背景颜色\n\n### wordcloud_font_path\n\n- 类型: `str`\n- 默认: 自带的字体（思源黑体）\n- 说明: 生成图片的字体文件位置\n\n### wordcloud_stopwords_path\n\n- 类型: `str`\n- 默认: 自带的停用词表\n- 说明: 生成图片的停用词表位置\n\n## 计划\n\n- [ ] 获取任意一天的词云\n',
    'author': 'hemengyang',
    'author_email': 'hmy0119@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/he0119/nonebot-plugin-wordcloud',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
