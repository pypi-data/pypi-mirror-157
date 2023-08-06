# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['InstallRelease', 'InstallRelease.temp', 'InstallRelease.temp.tmp']

package_data = \
{'': ['*'],
 'InstallRelease.temp': ['.ipynb_checkpoints/*'],
 'InstallRelease.temp.tmp': ['installs/*']}

install_requires = \
['python-magic>=0.4.27,<0.5.0', 'requests', 'rich', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['install-release = InstallRelease.cli:app']}

setup_kwargs = {
    'name': 'install-release',
    'version': '0.1.5',
    'description': '',
    'long_description': '# install-releases\n[![Python Version](https://img.shields.io/badge/Python-3.8_to_3.10-xx.svg)](https://shields.io/)\n\ninstall-releases is a cli tool to install tools based on your device info directly from github releases and keep them updated.\n\nThis can be any tool you want to install, which is pre-compiled for your device and present on github releases.\n\n> Also it\'s mainly for installing tools that are not available in the official repositories or package managers.\n\n```bash\n# Install install-releases\npip install -U install-release\n```\n\n```\n# Installing a tool named `gron` directly from github releases\n\n❯ get-release install https://github.com/tomnomnom/gron \n```\n\n![demo](.github/images/demo.png)\n\n\nChecking for gron is installed using installed-release:\n\n```\n❯ which gron\n/home/noobi/.release-bin/gron\n\n❯ gron --help\nTransform JSON (from a file, URL, or stdin) into discrete assignments to make it greppable\n... # more\n```\n\n## Prerequisites\n\n- python3.8 or higher\n\n- [libmagic](https://github.com/ahupp/python-magic#installation)\n- Default releases Installation Path is: `~/.release-bin/`,\nThis is the path where installed tools will get stored.\n\n- In order to run installed tools, you need to add the following line your `~/.bashrc` or `~/.zshrc` file:\n\n```bash\nexport PATH=$HOME/.release-bin:$PATH\n```\n\n\n## Install this package\n\n```bash\npip install -U install-release\n```\n\n\n### Example usage `get-release`\n\n\n```\n# Help page\n\n❯ get-release --help\nUsage: install-release [OPTIONS] COMMAND [ARGS]...\n\n  Github Release Installer, based on your system\n\n  Commands:\n    install  | Install github release, cli tool\n    ls       | list all installed release, cli tools\n    rm       | remove any installed release, cli tools\n    upgrade  | Upgrade all installed release, cli tools\n\n```\n\nFor sub command help use: `install-release <sub-command> --help`\n\nExample: `install-release get --help`\n\n\n\n#### Install tool from github releases\n\n```bash\n❯ install-release get "https://github.com/ahmetb/kubectx"\n\n📑 Repo     : ahmetb/kubectx\n🌟 Stars    : 13295\n✨ Language : Go\n🔥 Title    : Faster way to switch between clusters and namespaces in kubectl\n\n                              🚀 Install: kubectx                               \n┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓\n┃ Name    ┃ Selected Item                      ┃ Version ┃ Size Mb ┃ Downloads ┃\n┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩\n│ kubectx │ kubectx_v0.9.4_linux_x86_64.tar.gz │ v0.9.4  │ 1.0     │ 43811     │\n└─────────┴────────────────────────────────────┴─────────┴─────────┴───────────┘\nInstall this tool (Y/n): y\n INFO     Downloaded: \'kubectx_v0.9.4_linux_x86_64.tar.gz\' at /tmp/dn_kubectx_ph6i7dmk                                                               utils.py:159\n INFO     install /tmp/dn_kubectx_ph6i7dmk/kubectx /home/noobi/.release-bin/kubectx                                                                  core.py:132\n INFO     Installed: kubectx\n```\n```\n# checking if kubectx is installed\n❯ which kubectx\n/home/noobi/.release-bin/kubectx\n\n❯ kubectx --version\n0.9.4\n```\n\n#### List installed tools\n\n```bash\n❯ install-release ls\n\n                       Installed tools                        \n┏━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ Name      ┃ Version ┃ Url                                  ┃\n┡━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ terrascan │ v1.15.2 │ https://github.com/tenable/terrascan │\n│ gron      │ v0.7.1  │ https://github.com/tomnomnom/gron    │\n└───────────┴─────────┴──────────────────────────────────────┘    \n```\n\n#### Remove installed release\n\n```bash\n# Remove installed release\n\n❯ install-release rm gron\n    \nINFO     Removed: gron           \n```\n\n#### Update all previously installed tools to the latest version\n\n```bash\n❯ install-release upgrade\n\nFetching: https://github.com/tenable/terrascan\nUpdating: terrascan, v1.15.0 => v1.15.2\n INFO     Downloaded: \'terrascan_1.15.2_Linux_x86_64.tar.gz\' at /tmp/dn_terrascan_0as71a6v\n INFO     install /tmp/dn_terrascan_0as71a6v/terrascan /home/noobi/.release-bin/terrascan\n INFO     Installed: terrascan\n\nFetching: https://github.com/tomnomnom/gron\n INFO     No updates\n\nProgress... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 \n```\n\n',
    'author': 'Rishang',
    'author_email': 'rishangbhavsarcs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
