from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from locations.models import Division, District, Upazila
from .forms import ProfileForm, PrivacyForm


@login_required
def profile_view(request):
    """View your own profile."""
    profile = request.user.profile
    return render(request, 'profiles/view.html', {'profile': profile})


@login_required
def profile_edit(request):
    """Edit your own profile."""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profiles:view')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profiles/edit.html', {'form': form, 'profile': profile})


@login_required
def privacy_settings(request):
    """Manage privacy toggles."""
    profile = request.user.profile
    if request.method == 'POST':
        form = PrivacyForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy settings updated.')
            return redirect('profiles:privacy')
    else:
        form = PrivacyForm(instance=profile)
    return render(request, 'profiles/privacy.html', {'form': form})


# ============================================
# AJAX endpoints for cascading dropdowns
# ============================================
@require_GET
def load_districts(request):
    """Return districts for a given division_id."""
    division_id = request.GET.get('division_id')
    districts = District.objects.filter(division_id=division_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)


@require_GET
def load_upazilas(request):
    """Return upazilas for a given district_id."""
    district_id = request.GET.get('district_id')
    upazilas = Upazila.objects.filter(district_id=district_id).values('id', 'name')
    return JsonResponse(list(upazilas), safe=False)