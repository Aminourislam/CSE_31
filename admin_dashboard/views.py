from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from accounts.models import User

from .permissions import admin_required


# ============================================
# HOME / STATS
# ============================================
@admin_required
def home(request):
    total_members = User.objects.filter(role='MEMBER').count()
    pending = User.objects.filter(status='PENDING').count()
    approved = User.objects.filter(status='APPROVED').count()
    rejected = User.objects.filter(status='REJECTED').count()
    suspended = User.objects.filter(status='SUSPENDED').count()

    # These will be replaced when Events/Announcements apps are built
    total_events = 0
    total_announcements = 0
    upcoming_events = []
    recent_announcements = []

    recent_registrations = (
        User.objects
        .filter(role='MEMBER')
        .select_related('profile')
        .order_by('-created_at')[:8]
    )

    context = {
        'total_members': total_members,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'suspended': suspended,
        'total_events': total_events,
        'total_announcements': total_announcements,
        'recent_registrations': recent_registrations,
        'upcoming_events': upcoming_events,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'admin_dashboard/home.html', context)


# ============================================
# PENDING USERS
# ============================================
@admin_required
def pending_users(request):
    qs = (
        User.objects
        .filter(status='PENDING', role='MEMBER')
        .select_related('profile', 'profile__university', 'profile__department',
                        'profile__session', 'profile__batch', 'profile__district')
        .order_by('-created_at')
    )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/pending_users.html', {
        'page_obj': page_obj,
        'total_count': paginator.count,
    })


# ============================================
# ALL USERS
# ============================================
@admin_required
def users_list(request):
    qs = User.objects.select_related('profile').order_by('-created_at')

    status = request.GET.get('status', '')
    role = request.GET.get('role', '')
    search = request.GET.get('q', '').strip()

    if status:
        qs = qs.filter(status=status)
    if role:
        qs = qs.filter(role=role)
    if search:
        qs = qs.filter(
            Q(email__icontains=search) |
            Q(profile__full_name__icontains=search) |
            Q(profile__student_id__icontains=search)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/users_list.html', {
        'page_obj': page_obj,
        'total_count': paginator.count,
        'search': search,
        'selected_status': status,
        'selected_role': role,
        'status_choices': User.Status.choices,
        'role_choices': User.Role.choices,
    })


# ============================================
# USER DETAIL
# ============================================
@admin_required
def user_detail(request, user_id):
    target_user = get_object_or_404(
        User.objects.select_related(
            'profile', 'profile__university', 'profile__department',
            'profile__session', 'profile__batch',
            'profile__division', 'profile__district', 'profile__upazila',
        ),
        pk=user_id,
    )
    return render(request, 'admin_dashboard/user_detail.html', {'target_user': target_user})


# ============================================
# ACTIONS
# ============================================
def _change_status(user_id, new_status):
    user = get_object_or_404(User, pk=user_id)
    user.status = new_status
    user.save(update_fields=['status', 'updated_at'])
    return user


@admin_required
def approve_user(request, user_id):
    if request.method == 'POST':
        user = _change_status(user_id, 'APPROVED')
        messages.success(request, f'{user.email} has been approved.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:pending_users'))


@admin_required
def reject_user(request, user_id):
    if request.method == 'POST':
        user = _change_status(user_id, 'REJECTED')
        messages.warning(request, f'{user.email} has been rejected.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:pending_users'))


@admin_required
def suspend_user(request, user_id):
    if request.method == 'POST':
        user = _change_status(user_id, 'SUSPENDED')
        messages.warning(request, f'{user.email} has been suspended.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:users_list'))


@admin_required
def restore_user(request, user_id):
    if request.method == 'POST':
        user = _change_status(user_id, 'APPROVED')
        messages.success(request, f'{user.email} has been restored.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:users_list'))


@admin_required
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        email = user.email
        if user == request.user:
            messages.error(request, "You can't delete your own account.")
            return redirect('admin_dashboard:users_list')
        user.delete()
        messages.success(request, f'{email} has been deleted.')
        return redirect('admin_dashboard:users_list')
    return redirect('admin_dashboard:users_list')