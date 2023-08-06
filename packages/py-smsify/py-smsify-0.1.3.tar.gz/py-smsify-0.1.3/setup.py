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
    'version': '0.1.3',
    'description': 'Python library for creating GSM-7 compatible SMS messages',
    'long_description': '![](https://i.imgur.com/xuHAE49.png)\n# Python library for creating GSM-7 compatible SMS messages\n\n### Installation\n`pip install py-smsify`\n\n### Usage\n```python\nfrom py_smsify import SmsMessage\n\n#Encode to a string of valid characters\nmessage = SmsMessage("Gamer420").encoded_text\n# result: Gamer420\n\n#Encode to a python bytestring\nmessage = SmsMessage("Gamer420").encoded_bytes\n# result: b"Gamer420"\n\n#Encode with non latin languages\nmessage = SmsMessage("גיימר420").encoded_text\n# result: gyymr420\n\n#Encode with emojis\nmessage = SmsMessage("this 🎉 is 👏 phenomenal 🔥").encoded_text\n# result: "this :tada: is :clap: phenomenal :fire:"\n```\n\n### Message Stats\n```python\nfrom py_smsify import SmsMessage\n\n#Get message length in bytes\nmessage = SmsMessage("Gamer420").length\n# result: 8 bytes\nmessage = SmsMessage("Gamer{}420").length #{} are characters from the extended table and therefore require 2 bytes of space\n# result: 12 bytes\n\n#Get amount of segments the message will be split to\nmessage = SmsMessage("Gamer420").segments\n# result: 1 message\n\n#You can also have it calculate segment count with twilio message headers in mind\nmessage = SmsMessage("Gamer420",twilio=True).segments\n# result: 1 message\n\n```',
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
