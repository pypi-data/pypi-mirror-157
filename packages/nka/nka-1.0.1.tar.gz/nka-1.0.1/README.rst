========
Overview
========

Input Sequence Length
Transformer models like BERT / RoBERTa / DistilBERT etc. the runtime and the memory requirement grows quadratic with the input length. This limits transformers to inputs of certain lengths. A common value for BERT & Co. are 512 word pieces, which corresponde to about 300-400 words (for English). Longer texts than this are truncated to the first x word pieces.

By default, the provided methods use a limit fo 128 word pieces, longer inputs will be truncated. You can get and set the maximal sequence length like this:


.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/neural-keyword-assignment/badge/?style=flat
    :target: https://neural-keyword-assignment.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/tobibias/neural-keyword-assignment/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/tobibias/neural-keyword-assignment/actions

.. |version| image:: https://img.shields.io/pypi/v/nka.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/nka

.. |wheel| image:: https://img.shields.io/pypi/wheel/nka.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/nka

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/nka.svg
    :alt: Supported versions
    :target: https://pypi.org/project/nka

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/nka.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/nka

.. |commits-since| image:: https://img.shields.io/github/commits-since/tobibias/neural-keyword-assignment/v1.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/tobibias/neural-keyword-assignment/compare/v1.0.1...main



.. end-badges

An example package. Generated with cookiecutter-pylibrary.

* Free software: MIT license

Installation
============

::

    pip install nka

You can also install the in-development version with::

    pip install https://github.com/tobibias/neural-keyword-assignment/archive/main.zip


Documentation
=============


https://neural-keyword-assignment.readthedocs.io/


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
