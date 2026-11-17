from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from web.content import SITE
from web.models import Enquiry


class Command(BaseCommand):
    help = "Delete enquiries older than the retention period stated in the privacy notice."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show how many would be deleted, without deleting.")

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=30 * SITE["retention_months"])
        old = Enquiry.objects.filter(created_at__lt=cutoff)
        count = old.count()
        if options["dry_run"]:
            self.stdout.write(f"{count} enquiries are older than {SITE['retention_months']} months.")
            return
        old.delete()
        self.stdout.write(f"Deleted {count} enquiries older than {SITE['retention_months']} months.")
