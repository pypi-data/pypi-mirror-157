# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ttastromech', 'ttastromech.bin']

package_data = \
{'': ['*'], 'ttastromech': ['sounds/*']}

entry_points = \
{'console_scripts': ['astromechspeak = ttastromech.bin.astromechspeak:main']}

setup_kwargs = {
    'name': 'ttastromech',
    'version': '0.6.0',
    'description': 'python library transform text strings into Astromech (like R2D2) sounds',
    'long_description': '.. image:: https://raw.githubusercontent.com/MomsFriendlyRobotCompany/ttastromech/master/docs/pics/r2.gif\n\t:target: https://github.com/MomsFriendlyRobotCompany/ttastromech\n\nText to Astromech\n========================\n\n.. image:: https://img.shields.io/pypi/l/ttastromech.svg\n\t:target: https://github.com/MomsFriendlyRobotCompany/ttastromech\n.. image:: https://img.shields.io/pypi/pyversions/ttastromech.svg\n\t:target: https://github.com/MomsFriendlyRobotCompany/ttastromech\n.. image:: https://img.shields.io/pypi/wheel/ttastromech.svg\n\t:target: https://github.com/MomsFriendlyRobotCompany/ttastromech\n.. image:: https://img.shields.io/pypi/v/ttastromech.svg\n\t:target: https://github.com/MomsFriendlyRobotCompany/ttastromech\n\nThis was originally created by `Hugo SCHOCH <https://github.com/hug33k/PyTalk-R2D2>`_.\nI just packaged it on pypi and use it for an R2D2 project I am working on.\n\nIt works by assigning an R2-D2 sound to each letter of the alphabet, then, when you pass\nit a string, it makes sounds like an astromech. Currently it only supports Linux and\nmacOS.\n\n========= ================\nOS        Audio Program\n========= ================\nmacOS     ``afplay``\nlinux     ``play`` from libsox\nlinux     ``aplay`` from alsa\n========= ================\n\nInstall\n----------\n\nThe preferred method of installation is::\n\n\tpip install ttastromech\n\nUsage\n-------\n\n.. code-block:: python\n\n\tfrom ttastromech import TTAstromech\n\timport time\n\n\n\tif __name__ == \'__main__\':\n\t\tr2 = TTAstromech()\n\n\t\ttry:\n\t\t\tr2.run()  # make random astromech sounds by feeding it random strings of letters\n\t\t\ttime.sleep(2)\n\t\texcept KeyboardInterrupt:\n\t\t\tprint(\'bye ...\')\n\nOr::\n\n\tastromech.py "my god, its full of stars ... oh wait, the wrong movie"\n\nMIT License\n============\n\n**Copyright (c) 2015 SCHOCH Hugo**\n\n**Copyright (c) 2017 Kevin J. Walchko**\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/ttastromech/',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
