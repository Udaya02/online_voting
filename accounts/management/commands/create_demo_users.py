import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from accounts.models import VoterProfile


class Command(BaseCommand):
    help = "Create or update non-sensitive demo accounts for the hosted application."

    def handle(self, *args, **options):
        voter_username = os.getenv("DEMO_VOTER_USERNAME", "recruiter_voter")
        voter_email = os.getenv("DEMO_VOTER_EMAIL", "recruiter.voter@example.com")
        voter_password = os.getenv("DEMO_VOTER_PASSWORD")

        admin_username = os.getenv("DEMO_ADMIN_USERNAME", "recruiter_admin")
        admin_email = os.getenv("DEMO_ADMIN_EMAIL", "recruiter.admin@example.com")
        admin_password = os.getenv("DEMO_ADMIN_PASSWORD")

        if not voter_password or not admin_password:
            raise RuntimeError("DEMO_VOTER_PASSWORD and DEMO_ADMIN_PASSWORD must be configured")

        voter, _ = User.objects.get_or_create(
            username=voter_username,
            defaults={"email": voter_email},
        )
        voter.email = voter_email
        voter.is_active = True
        voter.is_staff = False
        voter.is_superuser = False
        voter.set_password(voter_password)
        voter.save()

        VoterProfile.objects.update_or_create(
            user=voter,
            defaults={
                "full_name": "Recruiter Demo Voter",
                "is_verified": True,
            },
        )

        admin, _ = User.objects.get_or_create(
            username=admin_username,
            defaults={"email": admin_email},
        )
        admin.email = admin_email
        admin.is_active = True
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(admin_password)
        admin.save()

        self.stdout.write(self.style.SUCCESS("Demo voter and admin accounts are ready."))
