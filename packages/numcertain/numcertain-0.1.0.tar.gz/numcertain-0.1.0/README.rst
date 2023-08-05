numcertain
===========================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

This package provides a python and numpy data type (`uncertain`) which implements a
floating point value with quantified uncertainity, allowing for forward uncertainity
propagation of uncorrelated values.

============== ==============================================================
PyPI           ``pip install numcertain``
Source code    https://github.com/garryod/numcertain
Documentation  https://garryod.github.io/numcertain
Releases       https://github.com/garryod/numcertain/releases
============== ==============================================================

A brief example of library usage is shown below:

.. code:: python

    from numpy import array
    from numcertain.uncertain import uncertain

    scalar = uncertain(42.0, 0.84)
    array_a = array([uncertain(1.0, 0.1), uncertain(2.0, 0.2)])
    array_b = array([3, 4]).astype(uncertain)

    print(f"scalar: {scalar}")
    print(f"array_a: {array_a}")
    print(f"array_b: {array_b}")

    print(f"array_a + array_b: {array_b + array_a}")
    print(f"array_b - array_a: {array_a - array_b}")
    print(f"array_a * array_b: {array_b * array_a}")
    print(f"array_a / array_b: {array_b / array_a}")

.. code:: bash

    scalar: 42.0±0.84
    array_a: [uncertain(1.0, 0.1) uncertain(2.0, 0.2)]
    array_b: [uncertain(3.0, 0.0) uncertain(4.0, 0.0)]
    array_a + array_b: [uncertain(4.0, 0.1) uncertain(6.0, 0.2)]
    array_b - array_a: [uncertain(-2.0, 3.1622776601683795) uncertain(-2.0, 4.47213595499958)]
    array_a * array_b: [uncertain(3.0, 0.30000000000000004) uncertain(8.0, 0.8)]
    array_a / array_b: [uncertain(3.0, 0.30000000000000004) uncertain(2.0, 0.2)]

.. |code_ci| image:: https://github.com/garryod/numcertain/workflows/Code%20CI/badge.svg?branch=master
    :target: https://github.com/garryod/numcertain/actions?query=workflow%3A%22Code+CI%22
    :alt: Code CI

.. |docs_ci| image:: https://github.com/garryod/numcertain/workflows/Docs%20CI/badge.svg?branch=master
    :target: https://github.com/garryod/numcertain/actions?query=workflow%3A%22Docs+CI%22
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/garryod/numcertain/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/garryod/numcertain
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/numcertain.svg
    :target: https://pypi.org/project/numcertain
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://garryod.github.io/numcertain for more detailed documentation.
