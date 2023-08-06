import os
import socket

from pathlib import Path

from django.conf import settings
from django.db.migrations.recorder import MigrationRecorder

from django_backup_utils.apps import BackupUtilsConfig


class MigrationNotFound(Exception):
    pass


def get_backup_name(filepath, hostname=None, projectname=None, all=False):
    if not isinstance(hostname, str):
        hostname = socket.gethostname()
    if not isinstance(projectname, str):
        projectname = BackupUtilsConfig.PROJECT_NAME
    splits = str(filepath).split("_")
    splits_hostname = Path(splits[0]).name
    splits_project = splits[1]

    if all:
        if str(filepath).endswith(".tar.gz") or str(filepath).endswith(".tar"):
            return filepath
    if hostname == splits_hostname and projectname == splits_project:
        if str(filepath).endswith(".tar.gz") or str(filepath).endswith(".tar"):
            return filepath


def get_system_migrations():
    f = MigrationRecorder.Migration.objects.all()
    unique_migration_dirs = set()
    system_migrations_migrated = 0
    system_migrations_files = 0

    for each in f.order_by('applied'):
        if Path(f"{settings.BASE_DIR}/{each.app}").is_dir():
            system_migrations_migrated += 1
            unique_migration_dirs.add(Path(f"{settings.BASE_DIR}/{each.app}"))

    for each in unique_migration_dirs:
        if Path(f"{each}/migrations/__init__.py").exists():
            for file in os.listdir(f"{each}/migrations/"):
                if file.endswith(".py") and not file.startswith('__init__'):
                    system_migrations_files += 1

    return system_migrations_migrated, system_migrations_files


def get_migration_file_list():
    f = MigrationRecorder.Migration.objects.all()
    migration_files = []
    not_found = []
    for each in f.order_by('applied'):
        if Path(f"{settings.BASE_DIR}/{each.app}").is_dir():
            if Path(f"{settings.BASE_DIR}/{each.app}/migrations/__init__.py").is_file():
                path = Path(f"{settings.BASE_DIR}/{each.app}/migrations/{each.name}.py")
                migration_files.append(path)
                if not path.is_file():
                    not_found.append(str(path.relative_to(settings.BASE_DIR)))

    if not_found:
        message = ""
        for each in not_found:
            message += str(each) + "\n"
        raise MigrationNotFound(message)

    return migration_files
