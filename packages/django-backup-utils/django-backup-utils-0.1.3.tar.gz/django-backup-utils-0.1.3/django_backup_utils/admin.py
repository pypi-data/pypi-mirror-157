from django.contrib import admin

from django_backup_utils import models


class BackupLogAdmin(admin.ModelAdmin):
    list_filter = ("module",)
    list_display = ("pk", "module", "message", "backup", "success", "executed_at", "system_migrations_migrated",
                    "system_migration_files", "dump_version", "system_version", "params")
    readonly_fields = ( "module", "message", "backup", "success", "executed_at", "system_migrations_migrated",
                        "system_migration_files", "dump_version", "system_version", "params", "output")

admin.site.register(models.BackupLog, BackupLogAdmin)