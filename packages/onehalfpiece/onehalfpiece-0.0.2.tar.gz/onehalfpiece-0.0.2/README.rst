学习如何给Python程序打包
===============================

Guide: https://pm.readthedocs.io/construction/build_opensource.html

修复的问题
* no pip.req 模块问题，修复办法 更改为 pip._internal.req 因为前者需要pip 9一下

如何上传到pypitest 和pypitest
* 需要安装twine
* 参考：https://dev.to/wangonya/publishing-your-python-packages-on-testpypi-before-publishing-on-pypi-2gb2



.. image:: https://travis-ci.org/ryanzhang/onehalfpiece.png
   :target: https://travis-ci.org/ryanzhang/onehalfpiece
   :alt: Build Status

.. .. image:: https://landscape.io/github/ryanzhang/onehalfpiece/master/landscape.png
..    :target: https://landscape.io/github/ryanzhang/onehalfpiece/master
..    :alt: Code Health

.. image:: https://coveralls.io/repos/ryanzhang/onehalfpiece/badge.png
   :target: https://coveralls.io/r/ryanzhang/onehalfpiece
   :alt: Coverage Status

Learn python how to package

* Free software: MIT license
* Documentation: http://onehalfpiece.rtfd.org/

Features
--------

TODO

Install
-------

::

   pip install onehalfpiece

Examples
--------

TODO

Changelog
---------

0.0.1
~~~~~~~~~~~~~~~~~~~~~~~~~~

2022-01-27

* init

Contributing
------------

::

   git clone git@github.com:ryanzhang/onehalfpiece.git
   cd onehalfpiece
   virtualenv .
   make

Credits
-------

* ryanzhang <ryanzhangcheng@gmail.com>

Add your name and email, detail in: https://github.com/ryanzhang/onehalfpiece/graphs/contributors

.. image:: https://d2weczhvl823v0.cloudfront.net/ryanzhang/onehalfpiece/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free
