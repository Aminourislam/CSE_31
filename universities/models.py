from django.db import models


class University(models.Model):
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_name or self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Universities'


class Department(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.university.short_name or self.university.name})"

    class Meta:
        ordering = ['name']
        unique_together = ['university', 'name']


class Session(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']


class Batch(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='batches')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='batches')

    def __str__(self):
        return f"{self.name} - {self.department.name}"

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'department', 'session']