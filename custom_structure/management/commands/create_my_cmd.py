# coding: utf-8
"""
:module: custom_commands.custom_structure.management.commands
:synopsis:

:moduleauthor: anthony
greau < anthony.greau.infogene @ axa - lifeinvest.com >
"""
import os

from custom_commands.custom_structure.lib.interactive import Interactive
from custom_commands.custom_structure.lib.manage_files import ManageFiles
from custom_commands.custom_structure.lib.manage_folders import ManageFolders
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    """
    help = "create custom command from CUSTOM_STRUCTURE['STRUCTURE_CMD'] structure"
    missing_args_message = "name option is mandatory"

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
            structure_cmd={},
            files_to_remove=[],
            packages_to_remove=[],
            files_to_add=[],
            packages_to_add=[]
        )
        self.settings_structure_cmd = settings.CUSTOM_STRUCTURE['STRUCTURE_CMD']

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
            '-p', '--path',
            dest='path',
            default=None,
            help='define if template folder will be created'
        )
        parser.add_argument(
            '-i', '--interactive',
            dest="interactive",
            default=False,
            action='store_true',
            help='define if user can select which action to do'
        )
        parser.add_argument(
            '-a', '--app',
            dest="app",
            default=False,
            action='store_true',
            help='define if customcommand is in app folder'
        )

    @staticmethod
    def check_validity(args, options):
        """
        """
        if not hasattr(settings, 'CUSTOM_STRUCTURE'):
            raise CommandError("CUSTOM_STRUCTURE")
        elif 'STRUCTURE_CMD' not in settings.CUSTOM_STRUCTURE.keys():
            raise CommandError("CUSTOM_STRUCTURE['STRUCTURE_CMD'] not found in settings")
        elif options['interactive']:
            if options['template'] or options['locale'] or options['command'] or options['path'] is not None:
                raise CommandError("interactive option can't be launch with other option")
        elif options['name'] == '' and not args:
            args = ['-h']
            opts = {}
            call_command('create_cmd', *args, **opts)

    def manage_cmd_folder(self, options):
        """

        :param options:
        :type options:
        :return:
        :rtype:
        """
        if options['path'] is None:
            cmd_folder = settings.BASE_DIR
            if 'cmd_folder' in self.settings_structure_cmd.keys():
                cmd_folder = self.settings_structure_cmd['cmd_folder']
        elif options['path'].startswith(settings.BASE_DIR):
            cmd_folder = options['path']
        else:
            cmd_folder = os.path.join(settings.BASE_DIR, options['path'])
        return cmd_folder

    def create_base_cmd(self, options):
        """
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

    def handle(self, *args, **options):
        """

        :param args:
        :type args:
        :param options:
        :type options:
        :return:
        :rtype:
        """
        structure_cmd = self.structure['structure_cmd']
        if options['verbosity'] >= 1:
            self.stdout.write(self.style.MIGRATE_HEADING("create custom command"))
        self.check_validity(args, options)
        if options['interactive']:
            self.interactive = Interactive(self.settings_structure_cmd)
            for action, fct in self.interactive.define_action().items():
                fct()
            self.structure = self.interactive.get_interactive_values()
        else:
            structure_cmd = self.settings_structure_cmd
            self.structure['path'] = self.manage_cmd_folder(options)
            self.structure['files_to_remove'] = structure_cmd['files_to_remove']
            self.structure['packages_to_remove'] = structure_cmd['packages_to_remove']
            self.structure['files_to_add'] = structure_cmd['files_to_add']
            self.structure['packages_to_add'] = self.structure['structure_cmd']['packages_to_add']
        self.target_folder = os.path.join(self.structure['path'], options['name'])
        if not options['app']:
            self.create_base_cmd(options)
            self.manage_files.update_apps_py(settings.BASE_DIR, self.target_folder, options)
        if 'files_to_remove' in structure_cmd.keys() and structure_cmd['files_to_remove']:
            self.manage_files.remove(self.target_folder, self.settings_structure_cmd['files_to_remove'])
        if 'packages_to_remove' in structure_cmd.keys() and structure_cmd['packages_to_remove']:
            self.manage_folders.remove(self.target_folder, self.settings_structure_cmd['packages_to_remove'])
        if 'files_to_add' in structure_cmd.keys() and structure_cmd['files_to_add']:
            self.manage_files.add(self.target_folder, self.settings_structure_cmd['files_to_add'])
        if 'packages_to_add' in structure_cmd.keys() and structure_cmd['packages_to_add']:
            self.manage_folders.add_packages(self.target_folder, self.settings_structure_cmd['packages_to_add'])
        if 'folders_to_add' in structure_cmd.keys() and structure_cmd['folders_to_add']:
            self.manage_folders.add_folder(self.target_folder, self.settings_structure_cmd['folders_to_add'])
