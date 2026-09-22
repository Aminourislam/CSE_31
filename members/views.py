from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.models import User
from profiles.models import Profile
from universities.models import University, Department, Session, Batch
from locations.models import Division, District, Upazila


# ============================================
# DASHBOARD
# ============================================
@login_required
def dashboard(request):
    """Member dashboard shown after login."""
    return render(request, 'members/dashboard.html', {'user': request.user})


# ============================================
# MEMBER DIRECTORY
# ============================================
def _approved_members_queryset():
    """Base queryset: only APPROVED members, with related data preloaded."""
    return (
        Profile.objects
        .filter(user__status=User.Status.APPROVED)
        .select_related(
            'user', 'university', 'department', 'session', 'batch',
            'division', 'district', 'upazila',
        )
        .order_by('full_name')
    )


@login_required
def directory(request):
    """Member directory with search, filters, and pagination."""

    qs = _approved_members_queryset()

    # ---------- Search ----------
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(full_name__icontains=search) |
            Q(student_id__icontains=search) |
            Q(organization__icontains=search) |
            Q(designation__icontains=search)
        )

    # ---------- Filters ----------
    university_id = request.GET.get('university', '')
    department_id = request.GET.get('department', '')
    session_id = request.GET.get('session', '')
    batch_id = request.GET.get('batch', '')
    division_id = request.GET.get('division', '')
    district_id = request.GET.get('district', '')
    upazila_id = request.GET.get('upazila', '')
    occupation = request.GET.get('occupation', '').strip()

    if university_id:
        qs = qs.filter(university_id=university_id)
    if department_id:
        qs = qs.filter(department_id=department_id)
    if session_id:
        qs = qs.filter(session_id=session_id)
    if batch_id:
        qs = qs.filter(batch_id=batch_id)
    if division_id:
        qs = qs.filter(division_id=division_id)
    if district_id:
        qs = qs.filter(district_id=district_id)
    if upazila_id:
        qs = qs.filter(upazila_id=upazila_id)
    if occupation:
        qs = qs.filter(occupation__icontains=occupation)

    # ---------- Pagination ----------
    paginator = Paginator(qs, 12)  # 12 cards per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ---------- Filter dropdown data ----------
    departments = Department.objects.filter(is_active=True)
    if university_id:
        departments = departments.filter(university_id=university_id)

    batches = Batch.objects.all()
    if department_id:
        batches = batches.filter(department_id=department_id)
    if session_id:
        batches = batches.filter(session_id=session_id)

    districts = District.objects.all()
    if division_id:
        districts = districts.filter(division_id=division_id)

    upazilas = Upazila.objects.all()
    if district_id:
        upazilas = upazilas.filter(district_id=district_id)

    context = {
        'page_obj': page_obj,
        'total_count': paginator.count,
        'search': search,
        'universities': University.objects.filter(is_active=True),
        'departments': departments,
        'sessions': Session.objects.filter(is_active=True),
        'batches': batches,
        'divisions': Division.objects.all(),
        'districts': districts,
        'upazilas': upazilas,
        'selected': {
            'university': university_id,
            'department': department_id,
            'session': session_id,
            'batch': batch_id,
            'division': division_id,
            'district': district_id,
            'upazila': upazila_id,
            'occupation': occupation,
        },
    }
    return render(request, 'members/directory.html', context)


# ============================================
# MEMBER DETAIL
# ============================================
@login_required
def member_detail(request, pk):
    """Show a single member's profile, respecting privacy settings."""
    profile = get_object_or_404(
        Profile.objects.select_related(
            'user', 'university', 'department', 'session', 'batch',
            'division', 'district', 'upazila',
        ),
        pk=pk,
        user__status=User.Status.APPROVED,
    )

    is_own_profile = (request.user == profile.user)

    return render(request, 'members/member_detail.html', {
        'profile': profile,
        'is_own_profile': is_own_profile,
    })