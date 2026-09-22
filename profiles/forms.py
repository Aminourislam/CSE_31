from django import forms
from .models import Profile

# Import at bottom to avoid circular import issues at module load
from locations.models import District, Upazila  # noqa: E402

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'full_name', 'profile_photo', 'gender', 'date_of_birth', 'blood_group',
            'phone',
            'university', 'department', 'student_id', 'session', 'batch',
            'division', 'district', 'upazila',
            'occupation', 'organization', 'designation',
            'facebook', 'linkedin', 'bio',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
            'batch': forms.Select(attrs={'class': 'form-select'}),
            'division': forms.Select(attrs={'class': 'form-select', 'id': 'id_division'}),
            'district': forms.Select(attrs={'class': 'form-select', 'id': 'id_district'}),
            'upazila': forms.Select(attrs={'class': 'form-select', 'id': 'id_upazila'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/...'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Empty querysets initially for cascade
        self.fields['district'].queryset = District.objects.none()
        self.fields['upazila'].queryset = Upazila.objects.none()

        # If editing existing profile, load dependent options
        if self.instance and self.instance.pk:
            if self.instance.division:
                self.fields['district'].queryset = District.objects.filter(
                    division=self.instance.division
                )
            if self.instance.district:
                self.fields['upazila'].queryset = Upazila.objects.filter(
                    district=self.instance.district
                )

            # Also filter departments by university
            if self.instance.university:
                self.fields['department'].queryset = self.fields['department'].queryset.filter(
                    university=self.instance.university
                )

        # Handle POST data (form resubmit)
        if 'division' in self.data:
            try:
                division_id = int(self.data.get('division'))
                self.fields['district'].queryset = District.objects.filter(division_id=division_id)
            except (ValueError, TypeError):
                pass

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['upazila'].queryset = Upazila.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                pass

        if 'university' in self.data:
            try:
                uni_id = int(self.data.get('university'))
                self.fields['department'].queryset = self.fields['department'].queryset.filter(
                    university_id=uni_id
                )
            except (ValueError, TypeError):
                pass


class PrivacyForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'phone_visibility',
            'email_visibility',
            'dob_visibility',
            'district_visibility',
            'upazila_visibility',
            'organization_visibility',
            'facebook_visibility',
            'linkedin_visibility',
        ]
        widgets = {
            'phone_visibility': forms.Select(attrs={'class': 'form-select'}),
            'email_visibility': forms.Select(attrs={'class': 'form-select'}),
            'dob_visibility': forms.Select(attrs={'class': 'form-select'}),
            'district_visibility': forms.Select(attrs={'class': 'form-select'}),
            'upazila_visibility': forms.Select(attrs={'class': 'form-select'}),
            'organization_visibility': forms.Select(attrs={'class': 'form-select'}),
            'facebook_visibility': forms.Select(attrs={'class': 'form-select'}),
            'linkedin_visibility': forms.Select(attrs={'class': 'form-select'}),
            }

