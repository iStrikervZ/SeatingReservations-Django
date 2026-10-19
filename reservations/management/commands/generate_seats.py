from django.core.management.base import BaseCommand
from reservations.models import Table, Seat


class Command(BaseCommand):
    help = "Generate initial 46 tables with 10 seats each"

    def handle(self, *args, **options):
        for n in range(1, 47):
            table, created = Table.objects.get_or_create(
                table_number=n
            )

            for i in range(1, 11):
                seat, created = Seat.objects.get_or_create(
                    table=table,
                    seat_number=i
                )
        self.stdout.write(self.style.SUCCESS("Seating layout generated successfully.")
)