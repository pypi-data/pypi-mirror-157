# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poste_sdk']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'pydantic>=1.9.1,<2.0.0', 'zmail>=0.2.8,<0.3.0']

setup_kwargs = {
    'name': 'poste-sdk',
    'version': '0.1.9',
    'description': '',
    'long_description': "## Poste-sdk\n\n> poste操作助手\n\n### Poste服务部署\n1. 生成文档 `cd docs && make html`\n2. [在线文档](https://poste-sdk.readthedocs.io)\n\n\n### 安装\n```\npip install poste-sdk\n```\n\n### 简要使用\n```python\nfrom poste_sdk.client import PosteClient\nfrom poste_sdk.client import BoxClient\nfrom poste_sdk.models import Mail\n\nwith PosteClient(address='管理账户', password='密码', domain='域名/ip', verify_ssl=False) as client:\n    # 初始化\n\n    box_client = client.init_box_client(email_prefix='test', password='test',domain=None) \n    assert isinstance(box_client, BoxClient)\n    # 获取最近1条邮件\n    mail = box_client.get_latest()\n    assert isinstance(mail, Mail)\n\n    # email 总数量\n    box_client.get_email_cnt()\n\n    # 获取指定邮件\n    mail = box_client.get_email(id_=1)\n    assert isinstance(mail, Mail)\n\n    # 删除邮件\n    box_client.delete_by_id(1)\n\n    # 清空邮件\n    box_client.drop_mails()\n```\n",
    'author': 'lishulong',
    'author_email': 'lishulong.never@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://poste-sdk.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
