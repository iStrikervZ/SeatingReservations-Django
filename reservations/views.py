from django.shortcuts import render, redirect
from .models import Reservation, Table, SeatAssignment, Seat


# Create your views here.
def reservation_login(request):
    if request.method == "POST":
        try:
            reservation_code = request.POST.get("reservation_code", "").strip().upper()

            reservation = Reservation.objects.get(reservation_code=reservation_code)
            request.session["reservation_id"] = reservation.id
            return redirect("table_selection")

        except Reservation.DoesNotExist:
            return render(request, 'reservations/reservation_login.html',{"error": "Reservation code not found"})

    return render(request, 'reservations/reservation_login.html')

def table_selection(request):
    reservation_id = request.session.get("reservation_id")
    reservation = Reservation.objects.get(id=reservation_id)

    tables = Table.objects.all()
    for table in tables:
        table.available_seats = table.seat_set.filter(seatassignment__isnull=True).count()

    return render(request, "reservations/table_selection.html", {"reservation": reservation, "tables": tables})

def seat_selection(request, table_id):
    if request.method == "POST":
        seat_id = request.POST.get("seat_id", "")
        seat = Seat.objects.get(id=seat_id)
        table = Table.objects.get(id=table_id)

        seats = table.seat_set.all()
        for seat in seats:
            seat.is_taken = SeatAssignment.objects.filter(seat=seat).exists()

        return render(request, "reservations/seat_selection.html", {"seats":seats, "table":table})