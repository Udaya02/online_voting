"""
Models for elections, candidates, and votes.
"""
import hashlib
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Election(models.Model):
    """
    Represents an election/poll with a defined voting period.
    Status is derived from start/end dates but can be manually overridden.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_elections')
    is_public = models.BooleanField(default=True, help_text='Whether results are visible to voters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'elections'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def computed_status(self):
        """Derive the current status based on dates and manual status."""
        if self.status == 'cancelled':
            return 'cancelled'
        now = timezone.now()
        if now < self.start_date:
            return 'upcoming'
        elif self.start_date <= now <= self.end_date:
            return 'active'
        else:
            return 'completed'

    @property
    def is_active(self):
        """Check if the election is currently accepting votes."""
        return self.computed_status == 'active' and self.status != 'cancelled'

    @property
    def is_upcoming(self):
        return self.computed_status == 'upcoming'

    @property
    def is_completed(self):
        return self.computed_status == 'completed'

    @property
    def total_votes(self):
        return self.votes.count()

    @property
    def total_candidates(self):
        return self.candidates.count()

    def time_remaining(self):
        """Return time remaining until election ends, or None if ended."""
        if self.is_active:
            delta = self.end_date - timezone.now()
            return delta
        return None

    def has_user_voted(self, user):
        """Check if a specific user has already voted in this election."""
        return self.votes.filter(voter=user).exists()


class Candidate(models.Model):
    """
    Represents a candidate in an election.
    Each candidate belongs to exactly one election.
    """
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=150)
    party = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    position_order = models.IntegerField(default=0, help_text='Display order on ballot')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candidates'
        ordering = ['position_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.election.title})"

    @property
    def vote_count(self):
        return self.votes.count()

    @property
    def vote_percentage(self):
        """Calculate percentage of total votes in the election."""
        total = self.election.total_votes
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)


class Vote(models.Model):
    """
    Represents a single vote cast by a voter for a candidate in an election.
    Enforces one-vote-per-election via unique constraint.
    Includes a SHA-256 hash for audit trail integrity.
    """
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_cast')
    voted_at = models.DateTimeField(auto_now_add=True)
    vote_hash = models.CharField(max_length=64, unique=True, editable=False)

    class Meta:
        db_table = 'votes'
        # Prevent double voting: each voter can only vote once per election
        unique_together = ('election', 'voter')
        ordering = ['-voted_at']

    def __str__(self):
        return f"{self.voter.username} → {self.candidate.name} ({self.election.title})"

    def save(self, *args, **kwargs):
        """Generate a SHA-256 vote hash for integrity verification."""
        if not self.vote_hash:
            raw = f"{self.election_id}-{self.voter_id}-{self.candidate_id}-{uuid.uuid4()}"
            self.vote_hash = hashlib.sha256(raw.encode()).hexdigest()
        super().save(*args, **kwargs)
