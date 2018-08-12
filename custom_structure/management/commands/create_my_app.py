# coding: utf-8
"""
:module: custom_commands.custom_structure.management.commands
:synopsis:

:moduleauthor: anthony
greau < anthony.greau.infogene @ axa - lifeinvest.com >
"""
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from custom_commands.custom_structure.lib.interactive import Interactive
from custom_commands.custom_structure.lib.manage_files import ManageFiles
from custom_commands.custom_structure.lib.manage_folders import ManageFolders


class Command(BaseCommand):
    """

    """
    help = "create custom application from CUSTOM_STRUCTURE['STRUCTURE_APP'] structure"
    missing_args_message = "name option is mandatory"
    requires_migrations_checks = True
    requires_system_checks = True

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        super(Command, self).__init__(*args, **kwargs)
        self.target = None
        self.interactive = None
        self.target_folder = None
        self.manage_files = ManageFiles()
        self.manage_folders = ManageFolders()
        self.structure = dict(
            path=None,
            structure_app={},
            files_to_remove=[],
            package_to_remove=[],
            files_to_add=[],
            packages_to_add=[]
        )
        self.settings_structure_app = settings.CUSTOM_STRUCTURE['STRUCTURE_APP']

    def manage_app_folder(self, options):
        """

        :param options:
        :type options:
        :return:
        :rtype:
        """
        if options['path'] is None:
            app_folder = settings.BASE_DIR
            if 'app_folder' in self.settings_structure_app.keys():
                app_folder = self.settings_structure_app['app_folder']
        elif options['path'].startwith(settings.BASE_DIR):
            app_folder = options['path']
        else:
            app_folder = os.path.join(settings.BASE_DIR, options['path'])
        return app_folder

    def create_base_app(self, options):
        """

        :param options:
        :type options:
        :return:
        :rtype:
        """
        if os.path.isdir(os.path.join(self.target_folder, options['name'])):
            raise CommandError(self.style.ERROR(
                "appliction {application_name} already exist in {path}".format(
                    application_name=options['name'], path=self.structure['path'])))
        else:
            os.mkdir(self.target_folder)
            args = [options['name']]
            opts = {
                'directory': self.target_folder,
            }
            call_command('startapp', *args, **opts)

    @staticmethod
    def check_validity(args, options):
        """
        """
        if not hasattr(settings, 'CUSTOM_STRUCTURE'):
            raise CommandError("CUSTOM_STRUCTURE")
        elif 'STRUCTURE_APP' not in settings.CUSTOM_STRUCTURE.keys():
            raise CommandError("CUSTOM_STRUCTURE['STRUCTURE_APP'] not found in settings")
        elif options['interactive']:
            if options['template'] or options['locale'] or options['command'] or options['path'] is not None:
                raise CommandError("interactive option can't be launch with other option")
        elif options['name'] == '' and not args:
            args = ['-h']
            opts = {}
            call_command('create_app', *args, **opts)

    def key_exist(self, key):
        """

        :param key:
        :type key:
        :return:
        :rtype:
        """
        if key in self.structure['structure_app'].keys() and self.structure['structure_app'][key]:
            return True
        return False

    def add_arguments(self, parser):
        """

        :param parser:
        :type parser:
        :return:
        :rtype:
        """
        parser.add_argument(
            'name',
            help='new application name'
        )
        parser.add_argument(
            '-i', '--interactive',
            dest="interactive",
            default=False,
            action='store_true',
            help='define if user can select which action to do'
        )
        parser.add_argument(
            '-t', '--template',
            dest='template',
            default=False,
            action='store_true',
            help='define if template folder will be created'
        )
        parser.add_argument(
            '-l', '--locale',
            dest='locale',
            default=False,
            action='store_true',
            help='define if locale folder will be created'
        )
        parser.add_argument(
            '-c', '--command',
            dest='command',
            default=False,
            action='store_true',
            help='integrate custom_command'
        )
        parser.add_argument(
            '-p', '--path',
            dest='path',
            default=None,
            help='define path of app creation'
        )

    def handle(self, *args, **options):
        """

        :param args:
        :type args:
        :param options:
        :type options:
        :return:
        :rtype:
        """
        self.check_validity(args, options)
        if options['interactive']:
            self.interactive = Interactive(self.settings_structure_app)
            for action, fct in self.interactive.define_action().items():
                fct()
            self.structure = self.interactive.get_interactive_values()
        else:
            self.structure['structure_app'] = self.settings_structure_app
            self.structure['path'] = self.manage_app_folder(options)
            self.structure['files_to_remove'] = self.structure['structure_app']['files_to_remove']
            self.structure['package_to_remove'] = self.structure['structure_app']['package_to_remove']
            self.structure['files_to_add'] = self.structure['structure_app']['files_to_add']
            self.structure['packages_to_add'] = self.structure['structure_app']['packages_to_add']
        self.target_folder = os.path.join(self.structure['path'], options['name'])
        self.create_base_app(options)
        self.manage_files.update_apps_py(settings.BASE_DIR, self.target_folder, options)
        if self.key_exist('files_to_remove'):
            self.manage_files.remove(self.target_folder, self.settings_structure_app['files_to_remove'])
        if self.key_exist('packages_to_remove'):
            self.manage_folders.remove(self.target_folder, self.settings_structure_app['packages_to_remove'])
        if self.key_exist('files_to_add'):
            self.manage_files.add(self.target_folder, self.settings_structure_app['files_to_add'])
        if self.key_exist('packages_to_add'):
            self.manage_folders.add_packages(self.target_folder, self.settings_structure_app['packages_to_add'])
        if self.key_exist('folders_to_add'):
            self.manage_folders.add_folder(self.target_folder, self.settings_structure_app['folders_to_add'])
        if options['template']:
            os.makedirs(os.path.join(self.target_folder, 'templates', args[0]))
        if options['locale']:
            for lang in settings.LANGUAGES:
                os.makedirs(os.path.join(self.target_folder, "locale", lang[0], "LC_MESSAGES"))
        if options['command']:
            args = [options['name']]
            opts = {
                'app': True,
                'path': self.structure['path'],
                'interactive': options['interactive']
            }
            call_command('create_my_cmd', *args, **opts)
