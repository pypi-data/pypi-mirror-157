# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['guiscrcpy',
 'guiscrcpy.install',
 'guiscrcpy.lib',
 'guiscrcpy.lib.bridge',
 'guiscrcpy.lib.bridge.audio',
 'guiscrcpy.lib.mapper',
 'guiscrcpy.network',
 'guiscrcpy.platform',
 'guiscrcpy.platform.windows_tools',
 'guiscrcpy.settings',
 'guiscrcpy.theme',
 'guiscrcpy.ui',
 'guiscrcpy.ui.pyqt5',
 'guiscrcpy.ui.pyside2',
 'guiscrcpy.ux']

package_data = \
{'': ['*'],
 'guiscrcpy': ['ts/*'],
 'guiscrcpy.ui': ['fonts/*', 'icons/*', 'rsrc/*', 'ui/*']}

install_requires = \
['QtPy>=1.9.0,<2.0.0',
 'black==22.3.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pynput==1.6.8']

extras_require = \
{':platform_system == "Windows"': ['pywin32==302'],
 'PyInstaller': ['PyInstaller'],
 'PyQt5': ['PyQt5>=5.15.4,<6.0.0'],
 'PySide2': ['PySide2>=5.15.2,<6.0.0']}

entry_points = \
{'console_scripts': ['guiscrcpy = guiscrcpy.cli:cli']}

setup_kwargs = {
    'name': 'guiscrcpy',
    'version': '2022.6.1',
    'description': 'A simple, pluggable, graphical user interface for the fastest Android screen mirroring software',
    'long_description': None,
    'author': 'Srevin Saju',
    'author_email': 'srevinsaju@sugarlabs.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
