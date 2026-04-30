"""
Account models for voter profiles and email verification.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class VoterProfile(models.Model):
    """
    Extended profile for each registered voter.
    Linked one-to-one with Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_profile')
    voter_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voter_profiles'
        verbose_name = 'Voter Profile'
        verbose_name_plural = 'Voter Profiles'

    def __str__(self):
        return f"{self.full_name} ({self.voter_id})"

    def save(self, *args, **kwargs):
        """Auto-generate a unique voter ID if not set."""
        if not self.voter_id:
            self.voter_id = f"VTR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class EmailVerificationToken(models.Model):
    """
    Token model for email verification during registration.
    Tokens expire after 24 hours.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_verification_tokens'

    def __str__(self):
        return f"Token for {self.user.username}"

    @property
    def is_expired(self):
        """Check if the token has expired (24 hour validity)."""
        return timezone.now() > self.created_at + timedelta(hours=24)
