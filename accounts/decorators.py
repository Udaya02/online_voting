"""
Custom decorators for access control.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator that restricts access to staff/admin users only.
    Redirects non-admin users to the voter dashboard with an error message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('voter_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def voter_required(view_func):
    """
    Decorator that restricts access to verified voters.
    Redirects unverified users to their profile page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if hasattr(request.user, 'voter_profile') and not request.user.voter_profile.is_verified:
            messages.warning(request, 'Please verify your email before voting.')
            return redirect('profile')
        return view_func(request, *args, **kwargs)
    return wrapper
