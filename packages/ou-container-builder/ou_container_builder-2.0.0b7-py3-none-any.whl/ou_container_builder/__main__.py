"""The main OU Container Builder commandline application.

Run ``ou-container-builder --help`` for help with the command-line parameters.
"""
import click
import os
import shutil
import subprocess

from jinja2 import Environment, PackageLoader
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from . import packs, core
from .validator import validate_settings
from .utils import merge_settings


def run_build(settings: dict, context: str, build: bool, clean: bool, tag: list) -> list:
    """Run the build process.

    This processes the ``settings``, generates the required files, and then runs the Docker build process.

    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :param context: The directory within which to run the build
    :type context: str
    :param build: Whether to automatically invoke ``docker build``
    :type build: bool
    :param clean: Whether to automatically clean all generated files
    :type clean: bool
    :param tag: A list of tags to pass to docker
    :type tag: list[str]
    :return: A list with any errors that occured during processing
    :rtype: list
    """
    settings = validate_settings(settings)
    if isinstance(settings, dict):
        env = Environment(loader=PackageLoader('ou_container_builder', 'templates'),
                          autoescape=False)

        if os.path.exists(os.path.join(context, 'ou-builder-build')):
            shutil.rmtree(os.path.join(context, 'ou-builder-build'))
        os.makedirs(os.path.join(context, 'ou-builder-build'))

        # Setup the core settings
        settings = merge_settings({
            'packages': {
                'apt': [
                    'sudo'
                ],
                'pip': [
                    'jupyter_server<2.0.0',
                    'jupyterhub<1.6.0'
                ]
            },
            'content': [
                {
                    'source': 'ou-builder-build/start.sh',
                    'target': '/usr/bin/start.sh',
                    'overwrite': 'always'
                },
                {
                    'source': 'ou-builder-build/jupyter_server_config.py',
                    'target': '/etc/jupyter/jupyter_server_config.py',
                    'overwrite': 'always'
                },
                {
                    'source': 'ou-builder-build/base.sudoers',
                    'target': '/etc/sudoers.d/99-home-dir',
                    'overwrite': 'always'
                }
            ],
            'scripts': {
                'build': [
                    {
                        'commands': [
                            'chmod a+x /usr/bin/start.sh'
                        ]
                    }
                ]
            }
        }, settings)

        # Handle optional packs
        if 'packs' in settings:
            for pack in settings['packs']:
                if pack['name'] == 'nbclassic':
                    settings = packs.nbclassic(context, env, settings, pack['options'])
                elif pack['name'] == 'tutorial-server':
                    settings = packs.tutorial_server(context, env, settings, pack['options'])
                elif pack['name'] == 'mariadb':
                    settings = packs.mariadb(context, env, settings, pack['options'])

        # Handle core packs
        settings = core.env(context, env, settings)
        if 'services' in settings:
            settings = core.services(context, env, settings)
        if 'scripts' in settings:
            settings = core.scripts(context, env, settings)
        if 'web_apps' in settings:
            settings = core.web_apps(context, env, settings)
        settings = core.content(context, env, settings)

        # Handle automatic hacks
        if 'packages' in settings and 'apt' in settings['packages']:
            if 'openjdk-11-jdk' in settings['packages']['apt']:
                if 'hacks' in settings:
                    if 'missing-man1' not in settings['hacks']:
                        settings['hacks'].append('missing-man1')
                else:
                    settings['hacks'] = ['missing-man1']

        settings = validate_settings(settings)
        if isinstance(settings, dict):
            # Sort package lists
            if 'packages' in settings:
                if 'apt' in settings['packages']:
                    settings['packages']['apt'].sort()
                if 'pip' in settings['packages']:
                    settings['packages']['pip'].sort()

            # Generate the Jupyter Server Config
            with open(os.path.join(context, 'ou-builder-build', 'jupyter_server_config.py'), 'w') as out_f:
                tmpl = env.get_template('jupyter_server_config.py')
                out_f.write(tmpl.render(**settings))

            # Generate the start script
            with open(os.path.join(context, 'ou-builder-build', 'start.sh'), 'w') as out_f:
                tmpl = env.get_template('start.sh')
                out_f.write(tmpl.render(**settings))

            # Generate the home-directory sudoers
            with open(os.path.join(context, 'ou-builder-build', 'base.sudoers'), 'w') as out_f:
                out_f.write(f'{settings["image"]["user"]} ALL=(ALL) NOPASSWD:/bin/chown {settings["image"]["user"]}\\:100 /home/{settings["image"]["user"]}/{settings["module"]["code"]}-{settings["module"]["presentation"]}\n')  # noqa: 501

            # Generate the Dockerfile
            with open(os.path.join(context, 'Dockerfile'), 'w') as out_f:
                tmpl = env.get_template('Dockerfile.jinja2')
                out_f.write(tmpl.render(**settings))

            if build:
                cmd = ['docker', 'build', context]
                if tag:
                    for t in tag:
                        cmd.append('--tag')
                        cmd.append(t)
                subprocess.run(cmd)
                if clean:
                    os.unlink(os.path.join(context, 'Dockerfile'))
                    if os.path.exists(os.path.join(context, 'ou-builder-build')):
                        shutil.rmtree(os.path.join(context, 'ou-builder-build'))
            return []
        else:
            return settings
    else:
        return settings


@click.command()
@click.option('-c', '--context',
              default='.',
              help='Context within which the container will be built',
              show_default=True)
@click.option('-b/-nb', '--build/--no-build',
              default=True,
              help='Automatically build the container',
              show_default=True)
@click.option('--clean/--no-clean',
              default=True,
              help='Automatically clean up after building the container',
              show_default=True)
@click.option('--tag',
              multiple=True,
              help='Automatically tag the generated image')
def main(context: str, build: bool, clean: bool, tag: list):
    """Build your OU Container."""
    with open(os.path.join(context, 'ContainerConfig.yaml')) as config_f:
        settings = load(config_f, Loader=Loader)
    result = run_build(settings, context, build, clean, tag)
    if result:
        click.echo(click.style('There are errors in your configuration settings:', fg='red'), err=True)
        click.echo(err=True)
        for error in settings:
            click.echo(error, err=True)


if __name__ == '__main__':
    main()
