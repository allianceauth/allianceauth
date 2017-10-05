#!/usr/bin/env python
import os
from optparse import OptionParser
from django.core.management import ManagementUtility


def create_project(parser, options, args):
    # Validate args
    if len(args) < 2:
        parser.error("Please specify a name for your Alliance Auth installation")
    elif len(args) > 3:
        parser.error("Too many arguments")

    project_name = args[1]
    try:
        dest_dir = args[2]
    except IndexError:
        dest_dir = None

    # Make sure given name is not already in use by another python package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        parser.error("'%s' conflicts with the name of an existing "
                     "Python module and cannot be used as a project "
                     "name. Please try another name." % project_name)

    print("Creating an Alliance Auth project called %(project_name)s" % {'project_name': project_name})  # noqa

    # Create the project from the Alliance Auth template using startapp

    # First find the path to Alliance Auth
    import allianceauth
    allianceauth_path = os.path.dirname(allianceauth.__file__)
    template_path = os.path.join(allianceauth_path, 'project_template')

    # Call django-admin startproject
    utility_args = ['django-admin.py',
                    'startproject',
                    '--template=' + template_path,
                    project_name]

    if dest_dir:
        utility_args.append(dest_dir)

    utility = ManagementUtility(utility_args)
    utility.execute()

    print("Success! %(project_name)s has been created" % {'project_name': project_name})  # noqa


def update_settings(parser, options, args):
    if len(args) < 2:
        parser.error("Please specify the path to your Alliance Auth installation")
    elif len(args) > 2:
        parser.error("Too many arguments")

    project_path = args[1]

    # find the target settings/base.py file, handing both the project and app as valid paths
    try:
        # given path is to the app
        settings_path = os.path.join(project_path, 'settings/base.py')
        assert os.path.exists(settings_path)
    except AssertionError:
        try:
            # given path is to the project, so find the app within it
            dirname = os.path.split(project_path)[-1]
            settings_path = os.path.join(project_path, dirname, 'settings/base.py')
            assert os.path.exists(settings_path)
        except AssertionError:
            parser.error("Unable to locate the Alliance Auth project at %s" % project_path)

    # first find the path to the Alliance Auth template settings
    import allianceauth
    allianceauth_path = os.path.dirname(allianceauth.__file__)
    template_path = os.path.join(allianceauth_path, 'project_template')
    template_settings_path = os.path.join(template_path, 'project_name/settings/base.py')

    # overwrite the local project's base settings
    print("Updating the settings at %s with the template at %s" % (settings_path, template_settings_path))
    with open(template_settings_path, 'r') as template, open(settings_path, 'w') as target:
        target.write(template.read())

    print("Successfully updated Alliance Auth settings.")


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
