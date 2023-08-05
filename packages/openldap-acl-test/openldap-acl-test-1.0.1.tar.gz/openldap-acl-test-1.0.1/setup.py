# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['openldap_acl_test']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['acltest = openldap_acl_test.cli:main']}

setup_kwargs = {
    'name': 'openldap-acl-test',
    'version': '1.0.1',
    'description': 'OpenLDAP ACL check tool',
    'long_description': '.. image:: https://github.com/mypaceshun/openldap-acl-test/actions/workflows/main.yml/badge.svg\n          :target: https://github.com/mypaceshun/openldap-acl-test/actions/workflows/main.yml\n.. image:: https://codecov.io/gh/mypaceshun/openldap-acl-test/branch/main/graph/badge.svg?token=1L16BLXJ74\n           :target: https://codecov.io/gh/mypaceshun/openldap-acl-test\n.. image:: https://readthedocs.org/projects/openldap-acl-test/badge/?version=latest\n           :target: https://openldap-acl-test.readthedocs.io/ja/latest/?badge=latest\n           :alt: Documentation Status\n\nOpenLDAP ACL Test\n=================\n\nOpenLDAPのACLをチェックを補助するツールです。\n設定ファイルをよみ、適切に ``slapacl`` コマンドを実行し、\n結果を記録します。\n\nInstall\n-------\n\n``pip`` コマンドを用いてPyPI経由でインストール可能です。\n\n::\n\n  pip install openldap-acl-test\n\nUsage\n-----\n\n``acltest`` というコマンドがインストールされます。\n\n::\n\n  $ acltest --help\n  Usage: acltest [OPTIONS]\n\n  Options:\n    -c, --conffile PATH  conffile path  [default: acltest_conf.yml]\n    --slapacl PATH       slapacl path  [default: /usr/sbin/slapacl]\n    --dry-run            dry run\n    -v, --verbose        verbose output\n    -h, --help           Show this message and exit.\n    --version            Show the version and exit.\n\n内部で ``slapacl`` を呼ぶので ``slapacl`` が実行可能な環境で実行する必要があります。\n',
    'author': 'KAWAI Shun',
    'author_email': 'mypaceshun@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mypaceshun/openldap-acl-test',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
