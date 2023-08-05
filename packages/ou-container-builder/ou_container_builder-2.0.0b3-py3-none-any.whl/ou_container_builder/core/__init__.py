"""Core settings processing functionality.

The core functionality covers

* :mod:`~ou_container_content.core.content`
* :mod:`~ou_container_content.core.env`
* :mod:`~ou_container_content.core.scripts`
* :mod:`~ou_container_content.core.services`
* :mod:`~ou_container_content.core.web_apps`

The functionality provided by these is processed after any packs are processed.
"""
from .content import apply_core as content  # noqa
from .env import apply_core as env  # noqa
from .scripts import apply_core as scripts  # noqa
from .services import apply_core as services  # noqa
from .web_apps import apply_core as web_apps  # noqa
