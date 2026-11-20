import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_social_autoposter.services import SocialSchedulerService


class Command(BaseCommand):
    help = (
        "Processes and dispatches due scheduled social media broadcasts and direct messages "
        "whose scheduled_at timestamp has arrived."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Show what scheduled posts/messages would be processed without executing them.",
        )
        parser.add_argument(
            '--broadcasts-only',
            action='store_true',
            help="Only process scheduled broadcasts (feed/page posts).",
        )
        parser.add_argument(
            '--messages-only',
            action='store_true',
            help="Only process scheduled direct messages (WhatsApp, Messenger, IG, X, LinkedIn).",
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help="Maximum number of items to process per run (default: 100).",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        broadcasts_only = options['broadcasts_only']
        messages_only = options['messages_only']
        limit = options['limit']

        start_time = timezone.now()
        prefix = "[DRY RUN] " if dry_run else ""

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"{prefix}Starting scheduled social posts & messages processor at {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
        )

        res = SocialSchedulerService.process_due_schedules(
            limit=limit,
            dry_run=dry_run,
            broadcasts_only=broadcasts_only,
            messages_only=messages_only
        )

        b_due = res['broadcasts_due']
        b_ok = res['broadcasts_processed']
        b_fail = res['broadcasts_failed']

        m_due = res['messages_due']
        m_ok = res['messages_processed']
        m_fail = res['messages_failed']

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Identified {b_due} scheduled broadcast(s) and {m_due} scheduled direct message(s) due for dispatch."
                )
            )
            return

        self.stdout.write(
            f"Broadcasts - Due: {b_due} | Processed: {b_ok} | Failed: {b_fail}"
        )
        self.stdout.write(
            f"Direct Messages - Due: {m_due} | Processed: {m_ok} | Failed: {m_fail}"
        )

        if res['errors']:
            self.stdout.write(self.style.ERROR(f"Encountered {len(res['errors'])} error(s):"))
            for err in res['errors']:
                self.stdout.write(self.style.ERROR(f"  - {err}"))

        if b_fail == 0 and m_fail == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully completed scheduled run. Total dispatched: {b_ok + m_ok}."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Run completed with errors. Dispatched: {b_ok + m_ok}, Failed: {b_fail + m_fail}."
                )
            )
