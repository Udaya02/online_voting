"""
Admin configuration for elections app.
"""
from django.contrib import admin
from .models import Election, Candidate, Vote


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'total_votes', 'created_by')
    list_filter = ('status', 'start_date', 'is_public')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'election', 'vote_count', 'position_order')
    list_filter = ('election',)
    search_fields = ('name', 'party')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'election', 'candidate', 'voted_at', 'vote_hash')
    list_filter = ('election', 'voted_at')
    search_fields = ('voter__username', 'vote_hash')
    readonly_fields = ('vote_hash', 'voted_at')
