from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.tasks import validate_services


class Command(BaseCommand):
    help = "Ensures all service accounts belong to users with required permissions."

    def handle(self, *args, **options):
        for u in User.objects.all():
            validate_services(u)
        self.stdout.write(self.style.SUCCESS('Verified all user service accounts.'))
