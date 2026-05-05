"""
Idempotently create the three demo accounts (freelancer, client, admin).

Usage:
    python manage.py seed_test_users

Re-running is safe: existing users are updated (password reset to the demo
value, role/flags realigned). Profiles are created via post_save signals.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


DEMO_USERS = [
    {
        "email": "freelancer@example.com",
        "username": "freelancer",
        "password": "freelancer123",
        "first_name": "Demo",
        "last_name": "Freelancer",
        "role": User.Role.FREELANCER,
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "client@example.com",
        "username": "client",
        "password": "client123",
        "first_name": "Demo",
        "last_name": "Client",
        "role": User.Role.CLIENT,
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "admin@example.com",
        "username": "admin",
        "password": "admin123",
        "first_name": "Demo",
        "last_name": "Admin",
        "role": User.Role.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
]


class Command(BaseCommand):
    help = "Create or update the three demo accounts (freelancer, client, admin)."

    def handle(self, *args, **options):
        for entry in DEMO_USERS:
            spec = dict(entry)
            password = spec.pop("password")
            email = spec["email"]
            user, created = User.objects.get_or_create(
                email=email,
                defaults=spec,
            )
            for field, value in spec.items():
                setattr(user, field, value)
            user.set_password(password)
            user.is_active = True
            user.is_verified = True
            user.save()
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb}: {email} ({spec['role']})"))

        self.stdout.write(self.style.SUCCESS("Done. Login credentials:"))
        for entry in DEMO_USERS:
            self.stdout.write(f"  {entry['email']}  /  {entry['password']}  ({entry['role']})")
