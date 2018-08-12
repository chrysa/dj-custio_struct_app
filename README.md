# TODO
    - refacto all code
    - add unit tests
    - pacakage plugins

# INSTALL
add this app and dict to your settings and enjoY

```
CUSTOM_STRUCTURE = {
    'STRUCTURE_APP': {
        'app_folder': os.path.join(BASE_SETTINGS.BASE_DIR, APP_FOLDER),
        'files_to_remove': [
            'models.py',
            'tests.py',
            'views.py'
        ],
        'package_to_remove': [],
        'packages_to_add': [
            'models',
            'views',
            'tests',
        ],
        'folders_to_add': [
            'fixtures',
            'templates/{}'.foramt(APP_FOLDER)
        ],
        'files_to_add': [
            'urls.py'
        ]
    },
    'STRUCTURE_CMD': {
        'cmd_folder': os.path.join(BASE_SETTINGS.BASE_DIR, CMD_FOLDER),
        'files_to_remove': [
            'admin.py',
            'models.py',
            'tests.py',
            'views.py'
        ],
        'packages_to_remove': [
            'migrations'
        ],
        'packages_to_add': [
            'tests',
            'management/commands',
        ],
        'files_to_add': []
    }
}
```