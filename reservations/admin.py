from django.contrib import admin

from reservations.models import Reservation, Table, Seat

# Register your models here.
admin.site.register(Reservation)
admin.site.register(Table)
admin.site.register(Seat)