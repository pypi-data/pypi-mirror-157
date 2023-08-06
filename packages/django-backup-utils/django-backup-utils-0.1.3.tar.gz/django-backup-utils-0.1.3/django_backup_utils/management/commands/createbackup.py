import os
import sys
import socket
import tarfile
import datetime
import subprocess

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from django_backup_utils import models
from django_backup_utils.apps import BackupUtilsConfig
from django_backup_utils.helpers import get_migration_file_list, get_system_migrations, MigrationNotFound

module = str(__name__).split(".")[-1]

NEWLINE = BackupUtilsConfig.NEWLINE


class Command(BaseCommand):

    def __init__(self):
        try:
            self.migrations = get_migration_file_list()
        except MigrationNotFound as e:
            print(f"{BackupUtilsConfig.FAIL}there are migration files missing on your system: ")
            print(e)
            exit()

        self.dump_migration_files = 0
        self.system_migrations_migrated, self.system_migration_files = get_system_migrations()
        self.json_path = Path(os.path.join(settings.BACKUP_ROOT, BackupUtilsConfig.JSON_FILENAME))
        self.dumpinfo_path = Path(os.path.join(settings.BACKUP_ROOT, BackupUtilsConfig.DUMPINFO))
        self.context = {'system_migrations_migrated': self.system_migrations_migrated}
        self.context['system_version'] = settings.BACKUP_SYSTEM_VERSION
        self.context['module'] = module
        super(Command, self).__init__()

    def make_tarfile(self, output_path: Path, compress: bool, source_dirs: list, source_files: list, migrations=[],
                     **kwargs):
        if compress:
            mode = "w:gz"
            suffix = ".tar.gz"
        else:
            mode = "w"
            suffix = ".tar"
        output_path = str(output_path) + suffix
        with tarfile.open(output_path, mode) as tar:
            for source_dir in source_dirs:
                print(f"add directory {source_dir} to tar: {output_path}")
                tar.add(source_dir, arcname=os.path.basename(source_dir))
            for source_file in source_files:
                print(f"add file {source_file} to tar: {output_path}")
                tar.add(source_file, arcname=os.path.basename(source_file))
            for migration in migrations:
                print(f"add file {migration} to tar: {output_path}")
                arcname = f"_migration_backup/{migration.relative_to(settings.BASE_DIR)}"
                tar.add(migration, arcname=arcname)
                self.dump_migration_files += 1
        if not Path(output_path).is_file():
            raise Exception("tarfile has not been created")
        return output_path

    def make_database_dump(self):

        print(f"{NEWLINE}creating database dump: {self.json_path}")
        with open(self.dumpinfo_path, 'w') as f:
            f.write(f"{settings.BACKUP_SYSTEM_VERSION}\n")
            f.write(f"{len(self.migrations)}")
        command = f"{sys.executable} {settings.BASE_DIR}/manage.py dumpdata --natural-foreign --natural-primary --indent 4 > {self.json_path}"
        output = subprocess.getoutput(command)
        if Path(self.json_path).is_file() and Path(self.dumpinfo_path).is_file():
            return Path(self.json_path), Path(self.dumpinfo_path)
        else:
            raise Exception("Error could not create database dump")

    def add_arguments(self, parser):
        parser.add_argument('--compress', action='store_true', help="compresses backup (.gz)")

    def handle(self, compress, *args, **options):

        self.context['params'] = str({'compress': compress})

        OUTPUT_DIR = Path(settings.BACKUP_ROOT)

        print(f"create new backup in {settings.BACKUP_ROOT}, compress = {compress}")
        if not OUTPUT_DIR.is_dir():
            print(f"{NEWLINE}creating output_dir {OUTPUT_DIR}")
            os.makedirs(OUTPUT_DIR, exist_ok=True)

        for path in settings.BACKUP_DIRS:
            posix = os.path.join(settings.BASE_DIR, path)
            posix = Path(posix)
            if not posix.is_dir():
                raise Exception(f"directory {posix} does not exist")

        if self.json_path.exists():
            print(f"{NEWLINE}clean up remaining {self.json_path}")
            os.remove(self.json_path)

        if self.dumpinfo_path.exists():
            print(f"{NEWLINE}clean up remaining {self.dumpinfo_path}")
            os.remove(self.dumpinfo_path)

        JSON_FILE, DUMPINFO_FILE = self.make_database_dump()
        TAR_PREFIX = str(socket.gethostname()) + "_" + BackupUtilsConfig.PROJECT_NAME + "_" + str(datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
        OUTPUT_TAR = Path(f"{OUTPUT_DIR}/{TAR_PREFIX}")
        OUTPUT_TAR = self.make_tarfile(output_path=OUTPUT_TAR,
                                       source_dirs=settings.BACKUP_DIRS,
                                       source_files=[JSON_FILE, DUMPINFO_FILE],
                                       migrations=self.migrations,
                                       compress=compress)

        self.context['backup'] = OUTPUT_TAR

        os.remove(Path(JSON_FILE).absolute())
        os.remove(Path(DUMPINFO_FILE).absolute())

        models.BackupLog.objects.create(message="created backup",
                                        dump_version=settings.BACKUP_SYSTEM_VERSION,
                                        system_migration_files=self.dump_migration_files,
                                        success=True,
                                        **self.context)
        print(
            f"{NEWLINE}{BackupUtilsConfig.GREEN}successfully created backup: {OUTPUT_TAR}, {Path(OUTPUT_TAR).stat().st_size / 1000 / 1000} MB")
