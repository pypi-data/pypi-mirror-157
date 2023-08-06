"""
Python Sequans Utilities
~~~~~~~~~~~~~~~~~~~~~~~~

pysequansutils provides tools for the Sequans Monarch 2 platform which
is used on Microchip cellular IoT development boards.

Overview
~~~~~~~~

pysequansutils is available:
    * install using pip from pypi: https://pypi.org/project/pysequansutils
    * browse source code on github: https://github.com/microchip-pic-avr-tools/pysequansutils
    * read API documentation on github: https://microchip-pic-avr-tools.github.io/pysequansutils
    * read the changelog on github: https://github.com/microchip-pic-avr-tools/pysequansutils/blob/main/CHANGELOG.md

Do a full firmware upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~
The `upgrade` module contains functions to do full firmware upgrades.

Full upgrade using bundled firmware:

.. code-block:: python

    from pysequansutils.upgrade import full_upgrade
    upgraded, active_version = full_upgrade()
    if upgraded:
        print(f"Successfully upgraded firmware to version '{active_version}'")
    else:
        print(f"Upgrade skipped. Current version is '{active_version}'")

Logging
~~~~~~~
This package uses the Python logging module for publishing log messages to
library users.  A basic configuration can be used (see example below), but for
best results a more thorough configuration is recommended in order to control
the verbosity of output from dependencies in the stack which also use logging.
See logging.yaml which is included in the package (although only used for CLI)

Simple logging configuration example:

.. code-block:: python

    import logging
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)

Dependencies
~~~~~~~~~~~~
pysequansutils depends on pykitcommander to manage Microchip IoT kit firmware
and connection.

pysequansutils depends on pyedbglib for its transport protocol.

pyedbglib requires a USB transport library like libusb. See pyedbglib package for more information.
"""

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
