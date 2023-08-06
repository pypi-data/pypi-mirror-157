"""Packs group together related settings and configuration files.

This contains the following optional packs:

* :mod:`~ou_container_content.packs.mariadb`
* :mod:`~ou_container_content.packs.nbclassic`
* :mod:`~ou_container_content.packs.tutorial_server`
"""
from .nbclassic import apply_pack as nbclassic  # noqa
from .mariadb import apply_pack as mariadb  # noqa
from .tutorial_server import apply_pack as tutorial_server  # noqa
