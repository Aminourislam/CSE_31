from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from events.models import Event, EventRegistration
from .permissions import admin_required
from .forms import EventForm


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