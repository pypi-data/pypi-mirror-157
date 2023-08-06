# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['findmydevice',
 'findmydevice.admin',
 'findmydevice.management',
 'findmydevice.management.commands',
 'findmydevice.migrations',
 'findmydevice.models',
 'findmydevice.views',
 'findmydevice_project',
 'findmydevice_project.settings',
 'findmydevice_project.tests']

package_data = \
{'': ['*'],
 'findmydevice': ['web/*', 'web/assets/*'],
 'findmydevice_project': ['templates/admin/*']}

install_requires = \
['bx_django_utils',
 'bx_py_utils',
 'colorlog',
 'django',
 'django-debug-toolbar',
 'django-tools']

entry_points = \
{'console_scripts': ['devshell = '
                     'findmydevice_project.dev_shell:devshell_cmdloop',
                     'run_testserver = '
                     'findmydevice_project.manage:start_test_server']}

setup_kwargs = {
    'name': 'django-fmd',
    'version': '0.0.1',
    'description': "Server for 'Find My Device' android app, implemented in Django/Python",
    'long_description': "# Django Find My Device\n\n![django-fmd @ PyPi](https://img.shields.io/pypi/v/django-fmd?label=django-fmd%20%40%20PyPi)\n![Python Versions](https://img.shields.io/pypi/pyversions/django-fmd)\n![License GPL V3+](https://img.shields.io/pypi/l/django-fmd)\n\nFind My Device Server implemented in Python using Django.\nUsable for the Andorid App: https://gitlab.com/Nulide/findmydevice\n\nPlan is to make is usable and create a [YunoHost package](https://gitlab.com/Nulide/findmydeviceserver/-/issues/9) for it.\n\n## State\n\nIt's in early developing stage and not really usable ;)\n\nWhat worked (a little bit) with Django's development server:\n\n* App can register the device\n* App can send a new location\n* App can delete all server data from the device\n* The Web page can fetch the location of a device\n\nTODOs:\n\n* Paginate between locations in Web page\n* Commands/Push/Pictures\n* Write tests, setup CI, deploy python package etc.\n\n\n## Start hacking:\n\n```bash\n~$ git clone https://gitlab.com/jedie/django-find-my-device.git\n~$ cd django-find-my-device\n~/django-find-my-device$ ./devshell.py\n...\n(findmydevice) run_testserver\n```\n\n## versions\n\n* [*dev*](https://gitlab.com/jedie/django-find-my-device/-/compare/11d09ecb...main)\n  * TBD v0.0.1\n",
    'author': 'JensDiemer',
    'author_email': 'git@jensdiemer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/jedie/django-find-my-device',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
