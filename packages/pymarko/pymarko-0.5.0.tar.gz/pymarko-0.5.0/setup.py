# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymarko']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pymarko',
    'version': '0.5.0',
    'description': 'A multicast framework and tools',
    'long_description': '# PyMarko\n\n**in development**\n\n## Example\n\n``` python\n#!/usr/bin/env python3\nfrom pymarko.udpsocket import Publisher\nfrom pymarko.udpsocket import Subscriber\nimport time\nimport sys\n\nHOST, PORT = "10.0.1.116", 9999\n\ndef pub():\n    pub = Publisher()\n    pub.info()\n    pub.clientaddr.append((HOST, PORT))\n    pub.clientaddr.append((HOST, 9998)) # this one will fail quietly\n\n    for _ in range(20):\n        msg = str(time.time()).encode("utf-8")\n        pub.publish(msg)\n\ndef sub():\n\n    def cb(data):\n        print(data)\n\n    try:\n        s = Subscriber()\n        s.bind(HOST, PORT)\n        s.info()\n        s.register_cb(cb)\n        s.loop()\n\n    except KeyboardInterrupt as e:\n        s.event = False\n        time.sleep(0.1)\n        print(e)\n        print("ctrl-z")\n\n\nif __name__ == "__main__":\n    if sys.argv[1] == "p":\n        pub()\n    elif sys.argv[1] == "s":\n        sub()\n```\n\n# MIT License\n\n**Copyright (c) 2018 Kevin J. Walchko**\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/pymarko/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
