"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from .models import VoterProfile, EmailVerificationToken


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    list_display = ('voter_id', 'full_name', 'user', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('voter_id', 'full_name', 'user__username', 'user__email')
    readonly_fields = ('voter_id', 'created_at', 'updated_at')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    readonly_fields = ('token', 'created_at')
