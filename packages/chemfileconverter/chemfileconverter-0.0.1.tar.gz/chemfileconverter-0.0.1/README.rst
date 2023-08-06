========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/chemfileconverter/badge/?style=flat
    :target: https://chemfileconverter.readthedocs.io/
    :alt: Documentation Status

.. |requires| image:: https://requires.io/github/CollinStark/chemfileconverter/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/CollinStark/chemfileconverter/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/CollinStark/chemfileconverter/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/CollinStark/chemfileconverter

.. |version| image:: https://img.shields.io/pypi/v/chemfileconverter.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/chemfileconverter

.. |wheel| image:: https://img.shields.io/pypi/wheel/chemfileconverter.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/chemfileconverter

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/chemfileconverter.svg
    :alt: Supported versions
    :target: https://pypi.org/project/chemfileconverter

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/chemfileconverter.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/chemfileconverter

.. |commits-since| image:: https://img.shields.io/github/commits-since/CollinStark/chemfileconverter/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/CollinStark/chemfileconverter/compare/v0.0.1...master



.. end-badges

A python converter for Chemical Table Files.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install chemfileconverter

You can also install the in-development version with::

    pip install https://github.com/CollinStark/chemfileconverter/archive/master.zip


Documentation
=============


https://chemfileconverter.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
