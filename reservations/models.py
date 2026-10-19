from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Reservation(models.Model):
    reservation_code = models.CharField(max_length=4, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    guest_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.reservation_code})"


class Table(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    def __str__(self):
        return f"Table {self.table_number}"

class Seat(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    def __str__(self):
        return f"Table {self.table.table_number} Seat {self.seat_number}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["table", "seat_number"],
                name="unique_seat_per_table",
            )
        ]

class SeatAssignment(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)

    def clean(self):
        current_seat_count = SeatAssignment.objects.filter(reservation=self.reservation).exclude(pk=self.pk).count()
        if current_seat_count >= self.reservation.guest_count:
            raise ValidationError("This reservation already has the maximum number of seats.")

    def __str__(self):
        return f"{self.reservation.first_name} {self.reservation.last_name} ({self.reservation.reservation_code}) - Table {self.seat.table.table_number} Seat {self.seat.seat_number}"

