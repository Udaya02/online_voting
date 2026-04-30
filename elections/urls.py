"""
URL patterns for the elections app.
Includes voter pages, admin pages, and API endpoints.
"""
from django.urls import path
from . import views, api_views

urlpatterns = [
    # ─── Voter Pages ────────────────────────────────────
    path('', views.voter_dashboard, name='home'),
    path('dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('election/<int:pk>/', views.election_detail, name='election_detail'),
    path('election/<int:pk>/vote/', views.voting_booth, name='voting_booth'),
    path('election/<int:pk>/results/', views.election_results, name='election_results'),

    # ─── Admin Pages ────────────────────────────────────
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/election/create/', views.create_election, name='create_election'),
    path('panel/election/<int:pk>/edit/', views.edit_election, name='edit_election'),
    path('panel/election/<int:pk>/delete/', views.delete_election, name='delete_election'),
    path('panel/election/<int:pk>/manage/', views.manage_election, name='manage_election'),
    path('panel/election/<int:election_pk>/candidate/add/', views.add_candidate, name='add_candidate'),
    path('panel/candidate/<int:pk>/edit/', views.edit_candidate, name='edit_candidate'),
    path('panel/candidate/<int:pk>/delete/', views.delete_candidate, name='delete_candidate'),

    # ─── API Endpoints ──────────────────────────────────
    path('api/election/<int:pk>/results/', api_views.api_election_results, name='api_election_results'),
    path('api/election/<int:pk>/turnout/', api_views.api_election_turnout, name='api_election_turnout'),
    path('api/admin/stats/', api_views.api_admin_stats, name='api_admin_stats'),
]
