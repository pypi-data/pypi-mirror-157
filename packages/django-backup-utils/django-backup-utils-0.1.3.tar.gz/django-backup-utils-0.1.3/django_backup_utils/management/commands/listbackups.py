import os
import time
import socket

from django.core.management.base import BaseCommand
from django.conf import settings

from django_backup_utils.apps import BackupUtilsConfig

from django_backup_utils.helpers import get_backup_name

NEWLINE = BackupUtilsConfig.NEWLINE


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--hostname', type=str, help="show backups for specified hostname")
        parser.add_argument('--projectname', type=str, help="show backups for specified django project")
        parser.add_argument('--all', action='store_true', help="show all backups")

    def handle(self, hostname, projectname, all, *args, **options):
        if os.path.exists(settings.BACKUP_ROOT):
            files = os.listdir(settings.BACKUP_ROOT)
            paths = [os.path.join(settings.BACKUP_ROOT, basename) for basename in files]
            correct = []
            if paths:
                paths.reverse()
                for each in paths:
                    file = get_backup_name(each, hostname, projectname, all)
                    if file:
                        correct.append(each)
                if correct:
                    for backup in correct:
                        print(f"{backup}\t\t{time.ctime(os.path.getctime(backup))}")
                else:
                    print(f"no backups found")
            else:
                print(f"no backups found")
        else:
            print(f"no backups have been created yet")
