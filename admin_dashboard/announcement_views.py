from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from announcements.models import Announcement
from .permissions import admin_required
from .forms import AnnouncementForm


@admin_required
def announcements_list(request):
    qs = Announcement.objects.select_related('created_by').order_by('-created_at')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(title__icontains=search)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/announcements/list.html', {
        'page_obj': page_obj,
        'search': search,
        'total_count': paginator.count,
    })


@admin_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, f'Announcement "{obj.title}" created.')
            return redirect('admin_dashboard:announcements_list')
    else:
        form = AnnouncementForm()

    return render(request, 'admin_dashboard/announcements/form.html', {
        'form': form,
        'title': 'Create Announcement',
        'action': 'Create',
    })


@admin_required
def announcement_edit(request, pk):
    obj = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Announcement "{obj.title}" updated.')
            return redirect('admin_dashboard:announcements_list')
    else:
        form = AnnouncementForm(instance=obj)

    return render(request, 'admin_dashboard/announcements/form.html', {
        'form': form,
        'title': f'Edit Announcement: {obj.title}',
        'action': 'Save',
        'announcement': obj,
    })


@admin_required
def announcement_delete(request, pk):
    obj = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        title = obj.title
        obj.delete()
        messages.success(request, f'Announcement "{title}" deleted.')
        return redirect('admin_dashboard:announcements_list')

    return render(request, 'admin_dashboard/announcements/confirm_delete.html', {'announcement': obj})


@admin_required
def announcement_toggle_publish(request, pk):
    obj = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        obj.is_published = not obj.is_published
        obj.save(update_fields=['is_published', 'updated_at'])
        state = 'published' if obj.is_published else 'unpublished'
        messages.success(request, f'"{obj.title}" {state}.')

    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:announcements_list'))