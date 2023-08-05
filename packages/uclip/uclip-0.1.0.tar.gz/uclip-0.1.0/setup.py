# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['uclip']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'b2sdk>=1.17.2,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'inquirerpy>=0.3.4,<0.4.0',
 'keyring>=23.6.0,<24.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'yaspin>=2.1.0,<3.0.0']

entry_points = \
{'console_scripts': ['uclip = uclip.main:uclip']}

setup_kwargs = {
    'name': 'uclip',
    'version': '0.1.0',
    'description': 'CLI Utility to upload clipboard images to B2 buckets',
    'long_description': '## UClip - Clipboard image uploader\n\n[![Build](https://github.com/ionite34/uclip/actions/workflows/build.yml/badge.svg)](https://github.com/ionite34/uclip/actions/workflows/build.yml)\n[![codecov](https://codecov.io/gh/ionite34/uclip/branch/main/graph/badge.svg?token=58XSRH3F26)](https://codecov.io/gh/ionite34/uclip)\n\n### Command line utility to upload a clipboard images to [B2 buckets][4]\n\n![](docs/demo.gif)\n\n> After upload, the displayed URL is also copied to the clipboard.\n\n### Install via pip or [pipx](https://github.com/pypa/pipx)\n```shell\npipx install uclip\n```\n\n### Run `--config` to set up your B2 API Keys and URL\n```shell\n> uclip --config\n? B2 Application ID: 0013770e41044120000000001\n? B2 Application Key: **********************\n? B2 Bucket Name: bucket-name\n? B2 Upload Path in Bucket: /screenshots/\n? Alternate URL: https://img.example.org/\n? File Name Length: 6\n```\n\n### The OS Keychain Service is used for secure API credential storage\n> The keychain can be set to always allow, or via biometric authentication by Touch ID or Windows Hello.\n\n| Windows                | MacOS         | Ubuntu LTS 20.04    |\n|------------------------|---------------|---------------------|\n| [Credential locker][1] | [Keychain][2] | [Secret Service][3] |\n\n[1]: https://docs.microsoft.com/en-us/windows/uwp/security/credential-locker\n[2]: https://developer.apple.com/documentation/security/certificate_key_and_trust_services/keys/storing_keys_in_the_keychain\n[3]: https://specifications.freedesktop.org/secret-service/latest/\n[4]: https://www.backblaze.com/b2/cloud-storage.html',
    'author': 'ionite34',
    'author_email': 'dev@ionite.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ionite34/uclip',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
