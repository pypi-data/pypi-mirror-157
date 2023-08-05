# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sharepoint']

package_data = \
{'': ['*']}

install_requires = \
['Office365-REST-Python-Client>=2.3.12,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'netlink-logging>=0.1.3,<0.2.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['sharepoint_list_info = '
                     'netlink.sharepoint.cli:print_list_info']}

setup_kwargs = {
    'name': 'netlink-sharepoint',
    'version': '0.0.3',
    'description': 'Tools to work with Sharepoint',
    'long_description': "# netlink-sharepoint\n\nTools to work with SharePoint\n\nFor now **Lists** are considered.\n\nInitial:\n\n- Script to help mapping:\n\n## `sharepoint_list_info`\n\n```shell\nUsage: sharepoint_list_info.py [OPTIONS] [NAME]...\n\n  Print information about SharePoint List(s)\n\n  NAME is not provided, all lists are returned.\n\nOptions:\n  -u, --url TEXT     Sharepoint URL\n  -i, --id TEXT      Client ID\n  -s, --secret TEXT  Client Secret\n  -t, --toml FILE    TOML file with 'url', 'id', and 'secret'\n  -f, --fields       include fields\n  --hidden           include hidden lists\n\n```\n\n\n## Roadmap\n\nNext:\n\n- subpackage to integrate with SQLAlchemy\n- define lists by subclassing \n\n\n## License\n\nMIT\n",
    'author': 'Bernhard Radermacher',
    'author_email': 'bernhard.radermacher@netlink-consulting.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/netlink-consulting/netlink-sharepoint',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
