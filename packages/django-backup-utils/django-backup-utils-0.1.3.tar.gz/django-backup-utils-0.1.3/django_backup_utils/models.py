from django.db import models

class BackupLog(models.Model,):

    backup = models.TextField()
    message = models.CharField(max_length=200)
    module = models.CharField(max_length=200)
    params = models.TextField(null=True, blank=True)

    system_version = models.TextField(null=True, blank=True)
    dump_version = models.TextField(null=True, blank=True)

    system_migrations_migrated = models.IntegerField("System Migrations", null=True, blank=True)
    system_migration_files = models.IntegerField("Dump Migration Files", null=True, blank=True)

    output = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BackupLog {self.pk}"
