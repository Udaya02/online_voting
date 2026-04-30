"""
Custom template tags and filters for the elections app.
"""
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def has_voted(election, user):
    """Check if a user has voted in an election. Usage: {% if election|has_voted:user %}"""
    return election.has_user_voted(user)


@register.filter
def percentage_of(value, total):
    """Calculate percentage. Usage: {{ count|percentage_of:total }}"""
    try:
        return round((int(value) / int(total)) * 100, 1) if int(total) > 0 else 0
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def time_until(dt):
    """Human-readable time until a datetime. Usage: {{ election.end_date|time_until }}"""
    if not dt:
        return ''
    delta = dt - timezone.now()
    if delta.total_seconds() < 0:
        return 'Ended'

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60

    if days > 0:
        return f"{days}d {hours}h remaining"
    elif hours > 0:
        return f"{hours}h {minutes}m remaining"
    else:
        return f"{minutes}m remaining"


@register.filter
def status_badge_class(status):
    """Return CSS class for status badge. Usage: {{ status|status_badge_class }}"""
    classes = {
        'active': 'badge-active',
        'upcoming': 'badge-upcoming',
        'completed': 'badge-completed',
        'cancelled': 'badge-cancelled',
        'draft': 'badge-draft',
    }
    return classes.get(status, 'badge-default')
