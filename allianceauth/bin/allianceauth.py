#!/usr/bin/env python
import os
import shutil
from optparse import OptionParser
from django.core.management import call_command
from django.core.management.commands.startproject import Command as BaseStartProject


class StartProject(BaseStartProject):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--python', help='The path to the python executable.')
        parser.add_argument('--celery', help='The path to the celery executable.')
        parser.add_argument('--gunicorn', help='The path to the gunicorn executable.')


def create_project(parser, options, args):
    # Validate args
    if len(args) < 2:
        parser.error("Please specify a name for your Alliance Auth installation.")
    elif len(args) > 3:
        parser.error("Too many arguments.")

    # First find the path to Alliance Auth
    import allianceauth
    allianceauth_path = os.path.dirname(allianceauth.__file__)
    template_path = os.path.join(allianceauth_path, 'project_template')

    # Determine locations of commands to render supervisor cond
    command_options = {
        'template': template_path,
        'python': shutil.which('python'),
        'gunicorn': shutil.which('gunicorn'),
        'celery': shutil.which('celery'),
        'extensions': ['py', 'conf', 'json'],
    }

    # Strip 'start' out of the arguments, leaving project name (and optionally destination dir)
    args = args[1:]

    # Call the command with extra context
    call_command(StartProject(), *args, **command_options)

    print("Success! %(project_name)s has been created." % {'project_name': args[0]})  # noqa


def update_settings(parser, options, args):
    if len(args) < 2:
        parser.error("Please specify the path to your Alliance Auth installation.")
    elif len(args) > 2:
        parser.error("Too many arguments.")

    project_path = args[1]
    project_name = os.path.split(project_path)[-1]

    # find the target settings/base.py file, handing both the project and app as valid paths
    # first check if given path is to the app
    settings_path = os.path.join(project_path, 'settings/base.py')
    if not os.path.exists(settings_path):
        # next check if given path is to the project, so the app is within it
        settings_path = os.path.join(project_path, project_name, 'settings/base.py')
        if not os.path.exists(settings_path):
            parser.error("Unable to locate the Alliance Auth project at %s" % project_path)

    # first find the path to the Alliance Auth template settings
    import allianceauth
    allianceauth_path = os.path.dirname(allianceauth.__file__)
    template_path = os.path.join(allianceauth_path, 'project_template')
    template_settings_path = os.path.join(template_path, 'project_name/settings/base.py')

    # overwrite the local project's base settings
    with open(template_settings_path, 'r') as template, open(settings_path, 'w') as target:
        target.write(template.read())

    print("Successfully updated %(project_name)s settings." % {'project_name': project_name})


COMMANDS = {
    'start': create_project,
    'update': update_settings,
}


def main():
    # Parse options
    parser = OptionParser(usage="Usage: %prog [start|update] project_name [directory]")
    (options, args) = parser.parse_args()

    # Find command
    try:
        command = args[0]
    except IndexError:
        parser.print_help()
        return

    if command in COMMANDS:
        COMMANDS[command](parser, options, args)
    else:
        parser.error("Unrecognised command: " + command)


if __name__ == "__main__":
    main()
