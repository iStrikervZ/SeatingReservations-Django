from django.db import models

# Create your models here.
class Reservation(models.Model):
    reservation_code = models.CharField(max_length=4, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    guest_count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.reservation_code})"


class Table(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    def __str__(self):
        return f"Table {self.table_number}"

class Seat(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField(unique=True)