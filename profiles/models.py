from django.db import models
from django.conf import settings
from PIL import Image
import os
import uuid


def profile_photo_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('profiles/', filename)


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    class Visibility(models.TextChoices):
        VISIBLE = 'VISIBLE', 'Visible'
        HIDDEN = 'HIDDEN', 'Hidden'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    full_name = models.CharField(max_length=200)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)

    phone = models.CharField(max_length=20, blank=True)

    university = models.ForeignKey('universities.University', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('universities.Department', on_delete=models.SET_NULL, null=True, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    session = models.ForeignKey('universities.Session', on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.ForeignKey('universities.Batch', on_delete=models.SET_NULL, null=True, blank=True)

    division = models.ForeignKey('locations.Division', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('locations.District', on_delete=models.SET_NULL, null=True, blank=True)
    upazila = models.ForeignKey('locations.Upazila', on_delete=models.SET_NULL, null=True, blank=True)

    occupation = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    designation = models.CharField(max_length=100, blank=True)

    facebook = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    # Privacy
    phone_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)
    email_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)
    dob_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.HIDDEN)
    district_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)
    upazila_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)
    organization_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)
    facebook_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)
    linkedin_visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.email})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_photo:
            try:
                img = Image.open(self.profile_photo.path)
                if img.height > 500 or img.width > 500:
                    img.thumbnail((500, 500))
                    img.save(self.profile_photo.path)
            except Exception:
                pass