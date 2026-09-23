from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Announcement


@login_required
def announcement_list(request):
    """List published announcements — newest first."""
    qs = Announcement.objects.filter(is_published=True)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'announcements/list.html', {
        'page_obj': page_obj,
    })


@login_required
def announcement_detail(request, pk):
    """View a single published announcement."""
    announcement = get_object_or_404(Announcement, pk=pk, is_published=True)
    return render(request, 'announcements/detail.html', {
        'announcement': announcement,
    })