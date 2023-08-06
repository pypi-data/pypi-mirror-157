# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parsuricata']

package_data = \
{'': ['*']}

modules = \
['test_parsuricata', 'LICENSE', 'CHANGELOG']
install_requires = \
['lark-parser>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'parsuricata',
    'version': '0.3.3',
    'description': 'Parse Suricata rules',
    'long_description': '# parsuricata\n\nParse Suricata rules\n\n\n# Installation\n\n```bash\npip install parsuricata\n```\n\n\n# Usage\n\n```python\nfrom parsuricata import parse_rules\n\nsource = \'\'\'\n  alert http $HOME_NET any -> !$HOME_NET any (msg: "hi mum!"; content: "heymum"; http_uri; sid: 1;)\n\'\'\'\n\nrules = parse_rules(source)\nprint(rules)\n#\n# alert http $HOME_NET any -> !$HOME_NET any ( \\\n#   msg: hi mum!; \\\n#   content: heymum; \\\n#   http_uri; \\\n#   sid: 1; \\\n# )\n\nrule = rules[0]\n\nprint(rule.action)\n# alert\n\nprint(rule.protocol)\n# http\n\nprint(rule.src)\n# $HOME_NET\n\nprint(rule.src_port)\n# any\n\nprint(rule.direction)\n# ->\n\nprint(rule.dst)\n# !$HOME_NET\n\nprint(rule.dst_port)\n# any\n\nfor option in rule.options:\n    print(f\'{option.keyword} = {option.settings}\')\n#\n# msg = hi mum!\n# content = heymum\n# http_uri = None\n# sid = 1\n```\n',
    'author': 'Zach "theY4Kman" Kanzler',
    'author_email': 'they4kman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theY4Kman/parsuricata',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
