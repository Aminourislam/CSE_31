from django.db import models


class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)
    bn_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class District(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    bn_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name}, {self.division.name}"

    class Meta:
        ordering = ['name']
        unique_together = ['division', 'name']


class Upazila(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='upazilas')
    name = models.CharField(max_length=100)
    bn_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name}, {self.district.name}"

    class Meta:
        ordering = ['name']
        unique_together = ['district', 'name']