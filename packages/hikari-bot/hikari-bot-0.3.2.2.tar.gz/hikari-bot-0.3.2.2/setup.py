# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src\\plugins'}

packages = \
['hikari_bot']

package_data = \
{'': ['*'], 'hikari_bot': ['template/*']}

install_requires = \
['Jinja2>=3.0.0,<4.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'httpx>=0.19.0',
 'nonebot-adapter-onebot>=2.1.0,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot-plugin-htmlrender>=0.1.0',
 'nonebot2>=2.0.0-beta.3',
 'nonebot_plugin_guild_patch>=0.2.0']

setup_kwargs = {
    'name': 'hikari-bot',
    'version': '0.3.2.2',
    'description': 'Nonebot2 HikariBot,支持战舰世界水表查询',
    'long_description': '<!-- markdownlint-disable MD033 MD041 -->\n<p align="center">\n  <a href="https://github.com/benx1n/HikariBot"><img src="https://s2.loli.net/2022/05/28/SFsER8m6TL7jwJ2.png" alt="Hikari " style="width:200px; height:200px" ></a>\n</p>\n\n<div align="center">\n\n# Hikari\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n战舰世界水表BOT\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  <a href="https://pypi.python.org/pypi/hikari-bot">\n    <img src="https://img.shields.io/pypi/v/hikari-bot" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.8.0+-blue" alt="python">\n  <a href="https://jq.qq.com/?_wv=1027&k=S2WcTKi5">\n    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-967546463-orange?style=flat-square" alt="QQ Chat Group">\n  </a>\n</p>\n\n## 简介\n\n战舰世界水表BOT，基于Nonebot2<br>\n水表人，出击！wws me recent！！！<br>\n如果觉得本插件还不错的话请点个Star哦~<br>\n[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)\n\n## 特色\n\n- [x] 账号总体、单船、近期战绩\n- [x] 全指令支持参数乱序\n- [x] 快速切换绑定账号\n- [x] 支持@快速查询\n- [x] 全异步，高并发下性能更优\n- [x] 支持频道（非官方bot类型）\n\n## 在Windows系统上快速部署\n[视频教程](https://www.bilibili.com/video/BV1r5411X7pr)\n\n1. 下载Hikari的[最新Release](https://github.com/benx1n/HikariBot/releases/download/Latest/release_windows.zip)并解压到合适文件夹\n2. 复制一份`.env.prod-example`文件，并将其重命名为`.env.prod`,打开并编辑\n   > ```\n   > API_TOKEN = xxxxxxxx #无需引号，TOKEN即回复您的邮件所带的一串由[数字+冒号+英文/数字]组成的字符串\n   >SUPERUSERS=["QQ号"]\n   > ```\n   >总之最后TOKEN应该长这样\n   >\n   >API_TOKEN = 123764323:ba1f2511fc30423bdbb183fe33\n   >\n   >只显示了.env，没有后面的后缀？请百度`windows如何显示文件后缀名`\n3. 双击`启动.bat`\n\n## 在Windows系统上完整部署\n1. 下载[Git](https://git-scm.com/download/win)、[Python](https://www.python.org/downloads/windows/)并安装\n    >Python版本需>3.8，或参考[Hoshino版插件](https://github.com/benx1n/wows-stats-bot)中使用Conda虚拟环境\n    >\n    >请注意python安装时勾选或点击`添加到环境变量`，可以安装后cmd中输入`python --version`来验证是否成功\n    >\n    >否则请自行百度如何添加python到环境变量\n\n3. 打开一个合适的文件夹，鼠标右键——Git Bash here，输入以下命令（任选一条）克隆本Hikari仓库\n   > ```\n   > git clone https://github.com/benx1n/HikariBot.git\n   >\n   > git clone https://gitee.com/benx1n/HikariBot.git\n   > ```\n3. 以管理员身份运行`一键安装.bat`\n\n   >执行下列两条命令安装nonebot2和hikari-bot插件\n   > ```\n   > pip install nb-cli\n   > pip install hikari-bot\n   > ```\n   >\n4. 复制一份`.env.prod-example`文件，并将其重命名为`.env.prod`,打开并编辑\n   > ```\n   > API_TOKEN = xxxxxxxx #无需引号，TOKEN即回复您的邮件所带的一串由[数字+冒号+英文/数字]组成的字符串\n   >SUPERUSERS=["QQ号"]\n   > ```\n   >总之最后应该长这样\n   >\n   >API_TOKEN = 123764323:ba1f2511fc30423bdbb183fe33\n   >\n   >只显示了.env，没有后面的后缀？请百度`windows如何显示文件后缀名`\n\n5. 双击`启动.bat`，在打开的浏览器中添加bot账号密码，重新启动Hikari\n    >打开终端，进入HikariBot文件夹下，输入下方命令运行bot\n    >```\n    >nb run\n    >```\n    >此时若没有报错，您可以打开http://127.0.0.1:8080/go-cqhttp/\n    >\n    >点击左侧添加账号，重启bot即可在网页上看到相应信息（大概率需要扫码）\n    >\n    >如果重启后go-cqhhtp一直卡在扫码或无限重启，请继续往下阅读\n\n\n## 在Ubuntu/Debian系统上的管理\n- 使用`./manage.sh`，基于原有批处理脚本\n- 无参数调用以获取使用帮助\n1. `install`\n    - 安装必须的依赖与bot本体\n2. `update`\n    - 更新bot\n3. `start [-t/--token] [token] [-i/--id] [qqid]`\n    - 运行bot\n    - 在当前目录下不存在`.env.prod`的情况下从参数获取token和qqid以创建相应文件，否则直接运行\n    - 考虑到使用Linux部署时多数情况下本地不存在图形界面，有风险的向公网开放访问\n    - 加入验证机制（listed）\n\n\n## 使用Docker部署\n- Docker目录下是一个简单的Dockerfile，可以基于官方的Python容器封装一个完整的HikariBot\n  - 以`12hydrogen/hikari-bot:latest`上线官方仓库\n- 注意需要将内部的8080端口映射出来\n  ```\n  docker run -d -P 12hydrogen/hikari-bot:latest -t [token] -i [qqid] # 首次使用需输入token和qqid，-P表示将8080端口随机映射至主机\n  docker run -d -p 12345:8080 12hydrogen/hikari-bot:latest -t [token] -i [qqid] # 使用-p以指定映射在外的端口\n  ```\n- 运行上述指令后会在终端显示一串字符，即Docker容器的标识符，一般使用前几位即可唯一确定一个容器\n  ```\n  1a2b3c4d5e..... # 标识符\n  docker stop 1a2b # 使用前四位确定，stop即停止容器\n  1a2b3c4d5e.....\n  docker start 1a2b # start即启动容器\n  1a2b3c4d5e.....\n  docker restart 1a2b # restart即重启容器\n  1a2b3c4d5e.....\n  ```\n- 在更新后即上传新版本容器\n  ```\n  docker pull 12hydrogen/hikari-bot:latest # 更新\n  docker stop 1a2b\n  1a2b...\n  docker rm 1a2b # 删除旧容器，\n  1a2b...\n  docker run -d -P 12hydrogen/hikari-bot:latest -t [token] -i [qqid] # 随机映射\n  docker run -d -p 12345:8080 12hydrogen/hikari-bot:latest -t [token] -i [qqid] # 指定映射\n  9z8y... # 注意标识符变化了\n  ```\n- 将配置文件与容器分离（listed）\n\n\n## 作为已有Bot的插件部署（如真寻、Haruka）\n1. 如果您已经有了一个基于Nonebot2的机器人（例如真寻），您可以直接\n    ```\n    pip install hikari-bot\n    ```\n2. 在bot的bot.py中加入\n    ```\n    nonebot.load_plugin(\'hikari_bot\')\n    ```\n3. 在环境文件中加入\n    ```\n    API_TOKEN = xxxxxxxxxxxx\n    SUPERUSERS=["QQ号"]\n    ```\n>一般来说该文件为.env.dev\n>\n>也有可能是.env.pord，具体需要看.env中是否有指定\n>\n>如果啥都不懂，bot.py里,在`nonebot.init()`下面加上\n>```\n>config = nonebot.get_driver().config\n>config.api_token = "xxxxxxxxxxxx"\n>```\n>请点击页面顶部链接加群获取Token哦~\n>\n4. 重启bot\n\n## 更新\n- Windows一键包：下载最新一键包，复制旧版本中`accounts`文件夹和`env.prod`文件替换至新版文件夹中即可\n- Bot版：以管理员身份运行`更新.bat`或执行`./manage.sh update`\n  >```\n  >pip install --upgrade hikari-bot\n  >git pull\n  >```\n- 插件版：pip install --upgrade hikari-bot\n>对比`.env.prod-example`中新增的配置项，并同步至你本地的`env.prod`\n>\n>install结束后会打印当前版本\n>\n>您也可以通过pip show hikari-bot查看\n>\n>如果没有更新到最新版请等待一会儿，镜像站一般每五分钟同步\n>\n\n\n  \n## 可能会遇到的问题\n\n### go-cqhttp扫码后提示异地无法登录\n>一般提示需要扫码，扫码后提示异地无法登录\n>\n>关于该问题，您可以查看[#1469](https://github.com/Mrs4s/go-cqhttp/issues/1469)获得相应解决办法，这里简单列举三种办法\n>\n>1. 启动时登录方式选择`浏览器滑条`，按后续提示登录\n>2. 手机下载`爱加速`等代理，连接到服务器对应市级地区\n>3. 在本地电脑使用go-cqhttp登录成功后，复制生成的`session.token`和`device.json`到服务器对应目录下，内嵌go-cqhttp为`account\\QQ号`，外置直接将整个本地文件夹拷贝过去即可，请注意使用外置go-cqhttp时需要将`.env.prod`的`USE_PLUGIN_GO_CQHTTP`的值改为`false`\n>\n\n### 无法使用内嵌go-cqhttp登录bot\n\n1. 下载 go-cqhttp 至合适的文件夹\n\n    - github 发布页：https://github.com/Mrs4s/go-cqhttp/releases\n\n    > 您需要根据自己的机器架构选择版本，Windows一般为x86/64架构，通常选择[go-cqhttp_windows_386.exe](https://github.com/Mrs4s/go-cqhttp/releases/download/v1.0.0-rc1/go-cqhttp_windows_386.exe)\n\n2. 双击go-cqhttp，提示释出bat，重新运行bat，选择websocket反向代理，go-cqhttp将会在同文件夹内自动创建一个`config.yml`，右键使用notepad++打开，根据注释填写QQ账号密码，并将以下内容写入文件结尾：\n\n    ```yaml\n      - ws-reverse:\n          universal: ws://127.0.0.1:8080/onebot/v11/ws\n          reconnect-interval: 5000\n          middlewares:\n            <<: *default\n    ```\n\n    > 关于go-cqhttp的配置，你可以在[这里](https://docs.go-cqhttp.org/guide/config.html#%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF)找到更多说明。\n\n3. 启动go-cqhttp，按照提示登录。\n\n\n4. 修改Hikari文件夹下.env.prod中`USE_PLUGIN_GO_CQHTTP`的值为`false`\n    ```\n    USE_PLUGIN_GO_CQHTTP = false\n    ```\n5. 在文件夹下打开终端，输入`nb run`启动bot\n\n\n### 出现ZoneInfoNotFoundError报错\n>\n>[issue#78](https://github.com/nonebot/nonebot2/issues/78)\n>\n### Recent和绑定提示\'鉴权失败\'\n1. 检查Token是否配置正确，token格式为`XXXXX:XXXXXX`\n2. 如果配置正确可能是Token失效了，请重新申请\n## 感谢\n\n[Nonebot2](https://github.com/nonebot/nonebot2)<br>\n[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)<br>\n[战舰世界API平台](https://wows.linxun.link/)<br>\n\n## 开源协议\n\nMIT\n',
    'author': 'benx1n',
    'author_email': 'shirakamikanade@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/benx1n/HikariBot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0',
}


setup(**setup_kwargs)
