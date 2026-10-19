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
    reservation_id = request.session.get("reservation_id")
    reservation = Reservation.objects.get(id=reservation_id)

    table = Table.objects.get(id=table_id)

    if request.method == "POST":
        seat_id = request.POST.get("seat_id", "")
        remove_seat_id = request.POST.get("remove_seat_id", "")

        print("seat_id", seat_id)
        print("remove_seat_id", remove_seat_id)

        # User clicked YOUR SEAT - REMOVE
        if remove_seat_id:
           deleted = SeatAssignment.objects.filter(
                seat_id=remove_seat_id,
                reservation=reservation
           ).delete()
           print("Deleted", deleted)

        # User clicked an AVAILABLE seat
        elif seat_id:
            seat = Seat.objects.get(
                id=seat_id,
                table=table
            )

            current_seat_count = SeatAssignment.objects.filter(
                reservation=reservation
            ).count()

            if current_seat_count < reservation.guest_count:
                SeatAssignment.objects.create(
                    seat=seat,
                    reservation=reservation
                )

    # Get all 10 seats belonging to this table
    seats = table.seat_set.all()

    # Determine how each seat should appear
    for seat in seats:
        seat.is_taken = SeatAssignment.objects.filter(
            seat=seat
        ).exists()

        seat.is_mine = SeatAssignment.objects.filter(
            seat=seat,
            reservation=reservation
        ).exists()

    return render(
        request,
        "reservations/seat_selection.html",
        {
            "seats": seats,
            "table": table
        }
    )