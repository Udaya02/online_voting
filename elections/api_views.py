"""
JSON API endpoints for real-time results and admin statistics.
Used by JavaScript for dynamic updates without full page reloads.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone

from .models import Election, Vote
from accounts.decorators import admin_required


@login_required
def api_election_results(request, pk):
    """
    API endpoint returning live vote counts for a specific election.
    Used by Chart.js on the results page for real-time updates.
    
    Returns JSON:
    {
        "election": { "title": ..., "status": ..., "total_votes": ... },
        "candidates": [
            { "id": ..., "name": ..., "party": ..., "votes": ..., "percentage": ... }
        ]
    }
    """
    election = get_object_or_404(Election, pk=pk)

    # Only allow viewing results for public elections or by admins
    if not election.is_public and not request.user.is_staff:
        return JsonResponse({'error': 'Results not available'}, status=403)

    candidates = election.candidates.annotate(
        total_votes=Count('votes')
    ).order_by('-total_votes')

    total_votes = election.total_votes

    candidate_data = []
    for c in candidates:
        percentage = round((c.total_votes / total_votes * 100), 1) if total_votes > 0 else 0
        candidate_data.append({
            'id': c.id,
            'name': c.name,
            'party': c.party,
            'votes': c.total_votes,
            'percentage': percentage,
        })

    return JsonResponse({
        'election': {
            'title': election.title,
            'status': election.computed_status,
            'total_votes': total_votes,
            'is_active': election.is_active,
        },
        'candidates': candidate_data,
    })


@admin_required
def api_admin_stats(request):
    """
    API endpoint returning overall platform statistics for admin dashboard.
    
    Returns JSON:
    {
        "total_elections": ...,
        "active_elections": ...,
        "total_votes": ...,
        "total_voters": ...,
        "recent_votes": [ { "election": ..., "time": ... } ]
    }
    """
    from django.contrib.auth.models import User
    now = timezone.now()

    total_elections = Election.objects.count()
    active_elections = Election.objects.filter(
        start_date__lte=now, end_date__gte=now, status__in=['active', 'draft']
    ).count()
    total_votes = Vote.objects.count()
    total_voters = User.objects.filter(is_staff=False).count()

    # Recent votes (last 10)
    recent = Vote.objects.select_related('election', 'voter').order_by('-voted_at')[:10]
    recent_votes = [{
        'election': v.election.title,
        'voter': v.voter.username,
        'time': v.voted_at.isoformat(),
    } for v in recent]

    return JsonResponse({
        'total_elections': total_elections,
        'active_elections': active_elections,
        'total_votes': total_votes,
        'total_voters': total_voters,
        'recent_votes': recent_votes,
    })


@admin_required
def api_election_turnout(request, pk):
    """
    API endpoint returning voter turnout data for a specific election.
    Groups votes by hour for timeline visualization.
    """
    election = get_object_or_404(Election, pk=pk)

    votes = election.votes.order_by('voted_at')
    turnout_data = []
    running_total = 0

    for vote in votes:
        running_total += 1
        turnout_data.append({
            'time': vote.voted_at.isoformat(),
            'total': running_total,
        })

    return JsonResponse({
        'election': election.title,
        'total_votes': running_total,
        'turnout': turnout_data,
    })
