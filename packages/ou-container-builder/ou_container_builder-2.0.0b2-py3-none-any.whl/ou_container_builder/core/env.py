"""Pack to handle setting up environment variables in the container."""
from jinja2 import Environment


def apply_core(context: str, env: Environment, settings: dict) -> dict:
    """Apply the env core.

    Does nothing.

    :param context: The context path within which the generation is running
    :type context: str
    :param env: The Jinja2 environment to use for loading and rendering templates
    :type env: :class:`~jinja2.environment.Environment`
    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :return: The updated settings
    :rtype: dict
    """
    return settings
