from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Event, EventRegistration


@login_required
def event_list(request):
    """List all published events. Newest first."""
    qs = Event.objects.filter(is_published=True).annotate(
        num_participants=Count('registrations')
    ).order_by('-created_at')

    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Which events is the current user registered for?
    my_registrations = set(
        EventRegistration.objects
        .filter(user=request.user)
        .values_list('event_id', flat=True)
    )

    return render(request, 'events/list.html', {
        'page_obj': page_obj,
        'my_registrations': my_registrations,
    })


@login_required
def event_detail(request, pk):
    """Show a single event."""
    event = get_object_or_404(Event, pk=pk, is_published=True)
    is_registered = EventRegistration.objects.filter(
        event=event, user=request.user
    ).exists()

    return render(request, 'events/detail.html', {
        'event': event,
        'is_registered': is_registered,
        'participants': event.registrations.select_related('user', 'user__profile'),
    })


@login_required
def register_for_event(request, pk):
    """Register the current user for an event."""
    event = get_object_or_404(Event, pk=pk, is_published=True)

    if request.method != 'POST':
        return redirect('events:detail', pk=event.pk)

    _, created = EventRegistration.objects.get_or_create(
        event=event, user=request.user
    )

    if created:
        messages.success(request, f'You are registered for "{event.title}".')
    else:
        messages.info(request, 'You are already registered for this event.')

    return redirect('events:detail', pk=event.pk)


@login_required
def cancel_registration(request, pk):
    """Cancel the current user's registration for an event."""
    event = get_object_or_404(Event, pk=pk, is_published=True)

    if request.method != 'POST':
        return redirect('events:detail', pk=event.pk)

    deleted, _ = EventRegistration.objects.filter(
        event=event, user=request.user
    ).delete()

    if deleted:
        messages.success(request, f'Your registration for "{event.title}" has been cancelled.')
    else:
        messages.info(request, 'You were not registered for this event.')

    return redirect('events:detail', pk=event.pk)