import os
import sys
import shutil
import tarfile
import subprocess

from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from django_backup_utils import models
from django_backup_utils.apps import BackupUtilsConfig
from django_backup_utils.helpers import get_migration_file_list, get_system_migrations, get_backup_name, MigrationNotFound

NEWLINE = BackupUtilsConfig.NEWLINE
module = str(__name__).split(".")[-1]


class LoadException(Exception):

    def __init__(self, message, output="", **kwargs):
        models.BackupLog.objects.create(message=message, output=str(output), success=False, **kwargs)
        super().__init__(message + f"\n{output}")


def extract_tar(input_filename, member_path="", strip=0):
    print(f"{NEWLINE}extracting {input_filename} to {settings.BASE_DIR}")

    if str(input_filename).endswith("tar.gz"):
        tar = tarfile.open(input_filename, "r:gz")
    elif str(input_filename).endswith("tar"):
        tar = tarfile.open(input_filename, "r:")

    if member_path:
        print(f"extract {member_path}")
        for member in tar.getmembers():
            if member_path in member.name:
                if not strip <= 0:
                    p = Path(member.path)
                    member.path = p.relative_to(*p.parts[:strip])
                    print(member.path)
                tar.extract(member, settings.BASE_DIR)
                print(f"extraction {member.name} to done")
    tar.close()


def load_database_dump(filepath, **kwargs):
    print(f"{NEWLINE}loading backup fixture {filepath.name}...")
    command = f"{sys.executable} manage.py loaddata {filepath}"
    output = subprocess.getoutput(command)
    print(output)
    if not "Installed" in output:
        raise LoadException(message=f"load_database_dump has failed", output=output, **kwargs)


def flush_db():
    print(f"{NEWLINE}flushing db...")
    command = f"{sys.executable} {settings.BASE_DIR}/manage.py flush --noinput"
    output = subprocess.getoutput(command)
    print("db has been flushed")


def delete_dir(dir, **kwargs):
    dir = Path(dir)
    shutil.rmtree(dir)
    if dir.exists():
        raise LoadException(message=f"delete_dir has failed", output=dir, **kwargs)
    else:
        print(f"deleted directory {dir}")


def latest_backup(backup_root):
    files = os.listdir(backup_root)
    paths = [os.path.join(backup_root, basename) for basename in files]

    applicable = []
    if paths:
        for each in paths:
            backup = get_backup_name(each)
            if backup:
                applicable.append(backup)
        return max(applicable, key=os.path.getctime)


def create_input():
    inp = input("continue y/N ? ")
    if str(inp) == "y" or str(inp) == "yes":
        return True


class Command(BaseCommand):

    def __init__(self):
        self.migrations = None
        self.migration_not_found = None
        try:
            self.migrations = get_migration_file_list()
        except MigrationNotFound as e:
            self.migration_not_found = e

        self.json_path = Path(os.path.join(settings.BASE_DIR, BackupUtilsConfig.JSON_FILENAME))
        self.dumpinfo_path = Path(os.path.join(settings.BASE_DIR, BackupUtilsConfig.DUMPINFO))
        self.system_migrations_migrated, self.system_migration_files = get_system_migrations()
        self.context = {'system_migrations_migrated': self.system_migrations_migrated}
        self.context['system_migration_files'] = None
        self.context['system_version'] = settings.BACKUP_SYSTEM_VERSION
        self.context['module'] = module
        super(Command, self).__init__()

    def add_arguments(self, parser):
        parser.add_argument('--tarpath', type=str, help='load the specified backup tarfile')
        parser.add_argument('--flush', action='store_true', help='flush the database (delete existing data)')
        parser.add_argument('--deletedirs', action='store_true',
                            help='delete all directories specified in settings.BACKUP_DIRS (before restoring)')
        parser.add_argument('--noinput', action='store_true', help='disable all prompts')
        parser.add_argument('--loadmigrations', action='store_true', help='restore all migration files')
        parser.add_argument('--skiptest', action='store_true', help='skip the unittest for loading database dump')

    def handle(self, tarpath, flush, deletedirs, noinput, loadmigrations, skiptest, *args, **options):

        self.context['params'] = str(
            {"flush": flush, "deletedirs": deletedirs, "noinput": noinput, "loadmigrations": loadmigrations,
             "skiptest": skiptest})

        if not tarpath:
            tar = latest_backup(settings.BACKUP_ROOT)
            if tar:
                tarpath = Path(tar)
                print(f"loading latest backup: {tarpath}, {tarpath.stat().st_size / 1000 / 1000} MB")
            else:
                print("nothing to load")
                return
        else:
            tarpath = Path(tarpath)
            print(f"loading given backup: {tarpath}, {tarpath.stat().st_size / 1000 / 1000} MB")

        self.context['backup'] = tarpath
        dump_info = tarfile.open(str(tarpath), "r")
        dump_info = dump_info.extractfile(f'{BackupUtilsConfig.DUMPINFO}').readlines()

        self.context['dump_version'] = dump_info[0].decode("UTF-8").strip()
        self.context['system_migration_files'] = int(dump_info[1].decode("UTF-8").strip())

        print(f"[dump-version (for)]  \t {self.context['dump_version']}")
        print(f"[system-version (now)]\t {self.context['system_version']}")
        print(f"[dump-migrations]     \t {self.context['system_migration_files']}")
        print(
            f"[system-migrations]   \t {self.system_migration_files} (found) / {self.context['system_migrations_migrated']} (applied)")

        if not loadmigrations:
            if self.migration_not_found:
                print(f"{BackupUtilsConfig.FAIL}there are migration files missing on your system:")
                print(self.migration_not_found)
                exit()

        if not noinput:
            result = create_input()
            if not result:
                print("abort")
                return

        if not tarpath.is_file():
            raise Exception(f"file {tarpath} does not exist")

        if loadmigrations:
            extract_tar(str(tarpath), "_migration_backup", strip=1)

        extract_tar(tarpath, member_path=BackupUtilsConfig.JSON_FILENAME)

        if not skiptest:
            print(f"{NEWLINE}running backup restore test ...\n{NEWLINE}")
            call_command('test', f"{BackupUtilsConfig.name}.tests.loaddata", interactive=False)

        if flush:
            flush_db()

        load_database_dump(self.json_path, **self.context)

        if deletedirs:
            print(f"{NEWLINE}trying to delete {settings.BACKUP_DIRS}...")
            for dir in settings.BACKUP_DIRS:
                delete_dir(dir, **self.context)

        # restore backup_dirs
        for each in settings.BACKUP_DIRS:
            extract_tar(tarpath, each)

        print(f"{NEWLINE}removing {self.json_path}")
        os.remove(self.json_path)

        if not self.json_path.exists():
            print(f"{NEWLINE}{BackupUtilsConfig.GREEN}successfully restored backup: {tarpath}")
            models.BackupLog.objects.create(message="loaded backup",
                                            success=True,
                                            **self.context)
