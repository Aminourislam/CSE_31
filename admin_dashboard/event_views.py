from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from events.models import Event, EventRegistration
from .permissions import admin_required
from .forms import EventForm

import csv
from django.http import HttpResponse
from django.utils import timezone

@admin_required
def events_list(request):
    qs = Event.objects.select_related('created_by').order_by('-created_at')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(title__icontains=search)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/events/list.html', {
        'page_obj': page_obj,
        'search': search,
        'total_count': paginator.count,
    })


@admin_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created.')
            return redirect('admin_dashboard:events_list')
    else:
        form = EventForm()

    return render(request, 'admin_dashboard/events/form.html', {
        'form': form,
        'title': 'Create Event',
        'action': 'Create',
    })


@admin_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated.')
            return redirect('admin_dashboard:events_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'admin_dashboard/events/form.html', {
        'form': form,
        'title': f'Edit Event: {event.title}',
        'action': 'Save',
        'event': event,
    })


@admin_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect('admin_dashboard:events_list')

    return render(request, 'admin_dashboard/events/confirm_delete.html', {'event': event})


@admin_required
def event_participants(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registrations = (
        EventRegistration.objects
        .filter(event=event)
        .select_related('user', 'user__profile')
        .order_by('-registered_at')
    )

    return render(request, 'admin_dashboard/events/participants.html', {
        'event': event,
        'registrations': registrations,
    })

@admin_required
def event_participants_export(request, pk):
    """Export participants of a single event as CSV."""
    event = get_object_or_404(Event, pk=pk)

    registrations = (
        EventRegistration.objects
        .filter(event=event)
        .select_related(
            'user',
            'user__profile',
            'user__profile__university',
            'user__profile__department',
            'user__profile__session',
            'user__profile__batch',
            'user__profile__division',
            'user__profile__district',
            'user__profile__upazila',
        )
        .order_by('user__profile__full_name')
    )

    # Safe filename: strip anything weird from event title
    safe_title = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in event.title)
    safe_title = safe_title.strip().replace(' ', '_')[:60]
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'event_{safe_title}_{timestamp}.csv'

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # BOM so Excel opens UTF-8 correctly
    response.write('\ufeff')

    writer = csv.writer(response)

    # --- Header row 1: Event info ---
    writer.writerow([f'Event: {event.title}'])
    if event.event_date:
        writer.writerow([f'Date: {event.event_date.strftime("%Y-%m-%d %H:%M")}'])
    if event.location:
        writer.writerow([f'Location: {event.location}'])
    writer.writerow([f'Total Participants: {registrations.count()}'])
    writer.writerow([f'Exported At: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])  # blank separator row

    # --- Header row 2: Column headers ---
    writer.writerow([
        '#',
        'Full Name',
        'Email',
        'Phone',
        'Student ID',
        'University',
        'Department',
        'Session',
        'Batch',

    ])

    # --- Data rows ---
    for idx, reg in enumerate(registrations.iterator(), start=1):
        p = reg.user.profile
        writer.writerow([
            idx,
            p.full_name or '',
            reg.user.email,
            p.phone or '',
            p.student_id or '',
            p.university.name if p.university else '',
            p.department.name if p.department else '',
            p.session.name if p.session else '',
            p.batch.name if p.batch else '',
            p.division.name if p.division else '',
            p.district.name if p.district else '',
            p.upazila.name if p.upazila else '',
            p.occupation or '',
            p.organization or '',
            p.designation or '',
            reg.registered_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response