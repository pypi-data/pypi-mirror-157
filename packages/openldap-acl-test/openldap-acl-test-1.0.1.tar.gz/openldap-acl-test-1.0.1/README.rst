.. image:: https://github.com/mypaceshun/openldap-acl-test/actions/workflows/main.yml/badge.svg
          :target: https://github.com/mypaceshun/openldap-acl-test/actions/workflows/main.yml
.. image:: https://codecov.io/gh/mypaceshun/openldap-acl-test/branch/main/graph/badge.svg?token=1L16BLXJ74
           :target: https://codecov.io/gh/mypaceshun/openldap-acl-test
.. image:: https://readthedocs.org/projects/openldap-acl-test/badge/?version=latest
           :target: https://openldap-acl-test.readthedocs.io/ja/latest/?badge=latest
           :alt: Documentation Status

OpenLDAP ACL Test
=================

OpenLDAPのACLをチェックを補助するツールです。
設定ファイルをよみ、適切に ``slapacl`` コマンドを実行し、
結果を記録します。

Install
-------

``pip`` コマンドを用いてPyPI経由でインストール可能です。

::

  pip install openldap-acl-test

Usage
-----

``acltest`` というコマンドがインストールされます。

::

  $ acltest --help
  Usage: acltest [OPTIONS]

  Options:
    -c, --conffile PATH  conffile path  [default: acltest_conf.yml]
    --slapacl PATH       slapacl path  [default: /usr/sbin/slapacl]
    --dry-run            dry run
    -v, --verbose        verbose output
    -h, --help           Show this message and exit.
    --version            Show the version and exit.

内部で ``slapacl`` を呼ぶので ``slapacl`` が実行可能な環境で実行する必要があります。
