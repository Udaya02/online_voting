"""
Views for voter-facing pages: dashboard, election details, voting booth, and results.
Also includes admin views for election and candidate management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Count, Q

from .models import Election, Candidate, Vote
from .forms import ElectionForm, CandidateForm
from accounts.decorators import admin_required, voter_required


# ─── Voter Views ────────────────────────────────────────────────────────────

@login_required
def voter_dashboard(request):
    """
    Main dashboard for voters showing active, upcoming, and completed elections.
    """
    now = timezone.now()

    active_elections = Election.objects.filter(
        start_date__lte=now, end_date__gte=now, status__in=['active', 'draft']
    ).annotate(vote_count=Count('votes'))

    upcoming_elections = Election.objects.filter(
        start_date__gt=now, status__in=['active', 'draft']
    ).annotate(vote_count=Count('votes'))

    completed_elections = Election.objects.filter(
        Q(end_date__lt=now) | Q(status='completed')
    ).annotate(vote_count=Count('votes'))[:5]

    # Get elections the user has voted in
    voted_election_ids = Vote.objects.filter(
        voter=request.user
    ).values_list('election_id', flat=True)

    context = {
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'completed_elections': completed_elections,
        'voted_election_ids': list(voted_election_ids),
        'total_votes_cast': voted_election_ids.count(),
    }
    return render(request, 'elections/dashboard.html', context)


@login_required
def election_detail(request, pk):
    """
    Show details of a specific election including candidates.
    """
    election = get_object_or_404(Election, pk=pk)
    candidates = election.candidates.all()
    has_voted = election.has_user_voted(request.user)

    context = {
        'election': election,
        'candidates': candidates,
        'has_voted': has_voted,
    }
    return render(request, 'elections/election_detail.html', context)


@login_required
@voter_required
def voting_booth(request, pk):
    """
    The voting booth where voters cast their ballots.
    Handles both displaying the ballot and processing votes.
    """
    election = get_object_or_404(Election, pk=pk)

    # Check if election is currently active
    if not election.is_active:
        messages.error(request, 'This election is not currently accepting votes.')
        return redirect('election_detail', pk=pk)

    # Check if user already voted
    if election.has_user_voted(request.user):
        messages.warning(request, 'You have already cast your vote in this election.')
        return redirect('election_results', pk=pk)

    candidates = election.candidates.all()

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')

        if not candidate_id:
            messages.error(request, 'Please select a candidate.')
            return render(request, 'elections/voting_booth.html', {
                'election': election, 'candidates': candidates
            })

        try:
            candidate = Candidate.objects.get(pk=candidate_id, election=election)
        except Candidate.DoesNotExist:
            messages.error(request, 'Invalid candidate selection.')
            return render(request, 'elections/voting_booth.html', {
                'election': election, 'candidates': candidates
            })

        try:
            Vote.objects.create(
                election=election,
                candidate=candidate,
                voter=request.user,
            )
            messages.success(request, 'Your vote has been recorded successfully!')
            return redirect('election_results', pk=pk)

        except IntegrityError:
            messages.error(request, 'You have already voted in this election.')
            return redirect('election_results', pk=pk)

    return render(request, 'elections/voting_booth.html', {
        'election': election,
        'candidates': candidates,
    })


@login_required
def election_results(request, pk):
    """
    Display election results with vote counts per candidate.
    Results are only shown if the election is public or if the user is admin.
    """
    election = get_object_or_404(Election, pk=pk)

    if not election.is_public and not request.user.is_staff:
        messages.warning(request, 'Results for this election are not publicly available yet.')
        return redirect('election_detail', pk=pk)

    candidates = election.candidates.annotate(
        total_votes=Count('votes')
    ).order_by('-total_votes')

    total_votes = election.total_votes
    has_voted = election.has_user_voted(request.user)

    context = {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes,
        'has_voted': has_voted,
    }
    return render(request, 'elections/results.html', context)


# ─── Admin Views ────────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    """
    Admin dashboard showing system overview, stats, and recent elections.
    """
    now = timezone.now()
    total_elections = Election.objects.count()
    active_elections = Election.objects.filter(
        start_date__lte=now, end_date__gte=now, status__in=['active', 'draft']
    ).count()
    total_votes = Vote.objects.count()

    from django.contrib.auth.models import User
    total_voters = User.objects.filter(is_staff=False).count()

    recent_elections = Election.objects.all()[:10]

    context = {
        'total_elections': total_elections,
        'active_elections': active_elections,
        'total_votes': total_votes,
        'total_voters': total_voters,
        'recent_elections': recent_elections,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def create_election(request):
    """Create a new election."""
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()
            messages.success(request, f'Election "{election.title}" created successfully!')
            return redirect('manage_election', pk=election.pk)
    else:
        form = ElectionForm()

    return render(request, 'admin_panel/election_form.html', {
        'form': form,
        'is_edit': False,
    })


@admin_required
def edit_election(request, pk):
    """Edit an existing election."""
    election = get_object_or_404(Election, pk=pk)

    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, f'Election "{election.title}" updated.')
            return redirect('manage_election', pk=pk)
    else:
        form = ElectionForm(instance=election)

    return render(request, 'admin_panel/election_form.html', {
        'form': form,
        'election': election,
        'is_edit': True,
    })


@admin_required
def delete_election(request, pk):
    """Delete an election (POST only)."""
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        title = election.title
        election.delete()
        messages.success(request, f'Election "{title}" has been deleted.')
        return redirect('admin_dashboard')
    return redirect('manage_election', pk=pk)


@admin_required
def manage_election(request, pk):
    """
    Manage a specific election: view details, candidates, and votes.
    """
    election = get_object_or_404(Election, pk=pk)
    candidates = election.candidates.annotate(total_votes=Count('votes')).order_by('-total_votes')
    total_votes = election.total_votes

    context = {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes,
    }
    return render(request, 'admin_panel/manage_election.html', context)


@admin_required
def add_candidate(request, election_pk):
    """Add a candidate to an election."""
    election = get_object_or_404(Election, pk=election_pk)

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            candidate.save()
            messages.success(request, f'Candidate "{candidate.name}" added.')
            return redirect('manage_election', pk=election_pk)
    else:
        form = CandidateForm()

    return render(request, 'admin_panel/candidate_form.html', {
        'form': form,
        'election': election,
        'is_edit': False,
    })


@admin_required
def edit_candidate(request, pk):
    """Edit an existing candidate."""
    candidate = get_object_or_404(Candidate, pk=pk)
    election = candidate.election

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, f'Candidate "{candidate.name}" updated.')
            return redirect('manage_election', pk=election.pk)
    else:
        form = CandidateForm(instance=candidate)

    return render(request, 'admin_panel/candidate_form.html', {
        'form': form,
        'election': election,
        'candidate': candidate,
        'is_edit': True,
    })


@admin_required
def delete_candidate(request, pk):
    """Delete a candidate (POST only)."""
    candidate = get_object_or_404(Candidate, pk=pk)
    election_pk = candidate.election.pk
    if request.method == 'POST':
        name = candidate.name
        candidate.delete()
        messages.success(request, f'Candidate "{name}" removed.')
    return redirect('manage_election', pk=election_pk)
