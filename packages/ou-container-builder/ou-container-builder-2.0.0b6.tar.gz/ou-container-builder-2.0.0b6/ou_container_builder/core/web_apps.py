"""Pack to handle web_apps setups."""
from jinja2 import Environment

from ..utils import merge_settings


def apply_core(context: str, env: Environment, settings: dict) -> dict:
    """Apply the web_apps core.

    This simply sets the server's default_path, if a web application is set as the default.

    :param context: The context path within which the generation is running
    :type context: str
    :param env: The Jinja2 environment to use for loading and rendering templates
    :type env: :class:`~jinja2.environment.Environment`
    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :return: The updated settings
    :rtype: dict
    """
    if len(settings['web_apps']) > 0:
        settings = merge_settings(settings, {
            'packages': {
                'pip': [
                    'jupyter-server-proxy>=3.2.1<4.0.0'
                ]
            }
        })
    for web_app in settings['web_apps']:
        if 'default' in web_app:
            settings = merge_settings(settings, {
                'server': {
                    'default_path': web_app['path']
                }
            })
    return settings
