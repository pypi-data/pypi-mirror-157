from pathlib import Path

from django.apps import AppConfig
from django.conf import settings

class BackupUtilsConfig(AppConfig):

    name = 'django_backup_utils'
    PROJECT_NAME = Path(settings.BASE_DIR).name
    JSON_FILENAME = 'django-backup-utils-fullbackup.json'
    DUMPINFO = 'django-backup-utils-backup-info.txt'

    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    NEWLINE = f"{BLUE}----------{ENDC}\n"
