# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsmaps']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jsmaps',
    'version': '0.1.2',
    'description': '',
    'long_description': "# Jsmaps:\n## Starting with Js maps\n* Creating a map:\n```py\njsmap = map_({'hi':'hello', 'wave':'hi'})\n ```\n* Basic showcase:\n>```py\n>from jsmaps import m #placeholder for map_\n>jsmap = m({'hi':'hello', 'wave':'hi', 0:'zero'})\n>print(jsmap)\n>#{\n>#    [0] [hi: hello]\n>#    [1] [wave: hi]\n>#    [2] [0: zero]\n>#}\n>```\n>```py\n>print(jsmap[1])\n>#hi\n>print(jsmap['hi'])\n>#hello\n>print(jsmap.get(0))\n>#zero\n>print(jsmap.pair(0))\n>#{'hi':'hello'}\n>print(jsmap.getpair(0))\n>#{2: 'zero'}   2 is the index in the map and zero is the value\n>jsmap[0] = 'bye'\n>#hi will now be bye\n>jsmap['wave'] = 'hand'\n>#wave will now be hand\n>```\n## Jsmaps Docs:\n### *.get(self, value):*\nLike `jsmap[value]` expect the `value` is always treated as a dict key.\n### _.pair(self, value, *, type_=dict):\nReturns the not specifed pair as a dict or list. \n\nFor example:\n```py\n#map has [1] [hi: hello]\n.pair(1) #{'hi':'hello'}\n.pair('hi') #{1:'hello'}\n.pair(1, type=list) ##['hi','hello']\n```\n### _.getpair(self, value, *, type_=dict):\nreturns the index and value of a key as a dict or list.\n```py\n#map has [2] [0: zero]\n.getpair(0) #{2: 'zero'}\n```\n### Tuple sets(beta)\n**Warning! beta. not completed.**\n\nGoal:\n```py\njsmap[key, slot] = value\njsmap[1, 1] = 'hi' #[1] ['hello':'hi'] is now [1] ['hi':'hi']\njsmap[1, 2] = 'hi' #[1] ['hi':'hello'] is now [1] ['hi':'hi']\njsmap[1, None] = {'hi': 'hi'} #[1] ['hello':'hello'] is now [1] ['hi':'hi']\n```",
    'author': 'I',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
