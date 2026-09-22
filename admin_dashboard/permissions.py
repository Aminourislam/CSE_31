from functools import wraps
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """Allow only ADMIN and SUPER_ADMIN users."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        if request.user.role not in ('ADMIN', 'SUPER_ADMIN'):
            raise PermissionDenied("You do not have access to the admin dashboard.")

        return view_func(request, *args, **kwargs)
    return _wrapped