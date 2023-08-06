# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_smsify']

package_data = \
{'': ['*']}

install_requires = \
['anyascii>=0.3.1,<0.4.0']

setup_kwargs = {
    'name': 'py-smsify',
    'version': '0.1.1',
    'description': 'Python library for creating GSM-7 compatible SMS messages',
    'long_description': '![](https://i.imgur.com/xuHAE49.png)\n# Python library for creating GSM-7 compatible SMS messages\n\n###Installation\n`pip install py-smsify`\n\n###Usage\n```python\nfrom py_smsify import SmsMessage\n\n#Encode to a string of valid characters\nmessage = SmsMessage("Gamer420").encoded_text\n# result: Gamer420\n\n#Encode to a python bytestring\nmessage = SmsMessage("Gamer420").encoded_bytes\n# result: b"Gamer420"\n\n#Encode with non latin languages\nmessage = SmsMessage("גיימר420").encoded_text\n# result: gyymr420\n\n#Encode with emojis\nmessage = SmsMessage("this 🎉 is 👏 phenomenal 🔥").encoded_text\n# result: "this :tada: is :clap: phenomenal :fire:"\n```',
    'author': 'Simon Wissotsky',
    'author_email': 'Wissotsky@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SkyDiverCool/py-smsify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
