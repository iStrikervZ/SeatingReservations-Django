from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
from django.contrib import messages
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

    if not reservation_id:
        return redirect("reservation_login")

    reservation = Reservation.objects.get(id=reservation_id)

    if reservation.is_confirmed:
        return redirect("confirmation")

    tables = Table.objects.all()
    for table in tables:
        table.available_seats = table.seat_set.filter(seatassignment__isnull=True).count()

    return render(request, "reservations/table_selection.html", {"reservation": reservation, "tables": tables})

def seat_selection(request, table_id):
    reservation_id = request.session.get("reservation_id")
    if not reservation_id:
        return redirect("reservation_login")

    reservation = Reservation.objects.get(id=reservation_id)

    if reservation.is_confirmed:
        return redirect("confirmation")

    table = Table.objects.get(id=table_id)

    if request.method == "POST":
        seat_id = request.POST.get("seat_id", "")
        remove_seat_id = request.POST.get("remove_seat_id", "")

        if remove_seat_id:
           SeatAssignment.objects.filter(
                seat_id=remove_seat_id,
                reservation=reservation
           ).delete()

           return redirect(
               "seat_selection", table_id=table_id)


        elif seat_id:
            try:
                with transaction.atomic():
                    locked_reservation = Reservation.objects.select_for_update().get(
                        id=reservation_id
                    )


                    seat = Seat.objects.select_for_update().get(
                        id=seat_id,
                        table=table
                    )

                    current_seat_count = SeatAssignment.objects.filter(
                        reservation=locked_reservation
                    ).count()

                    seat_is_taken = SeatAssignment.objects.filter(seat=seat).exists()

                    if seat_is_taken:
                        messages.error(request, "This seat was reserved by another guest. Please choose another seat.")
                        return redirect("seat_selection", table_id=table_id)


                    elif current_seat_count >= locked_reservation.guest_count:
                        messages.error(request, "You have already selected the maximum number of seats.")
                        return redirect("seat_selection", table_id=table_id)

                    else:
                        SeatAssignment.objects.create(
                            seat=seat,
                            reservation=locked_reservation
                        )
                        return redirect(
                            "seat_selection", table_id=table_id)

            except IntegrityError:
                messages.error(request, "This seat was reserved by another guest. Please choose another seat.")
                return redirect("seat_selection", table_id=table_id)

    selected_seat_count = SeatAssignment.objects.filter(reservation=reservation).count()
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
            "table": table,
            "reservation":reservation,
            "selected_seat_count": selected_seat_count,
        }
    )

def review_reservation(request):
    reservation_id = request.session.get("reservation_id")

    if not reservation_id:
        return redirect("reservation_login")

    reservation = Reservation.objects.get(id=reservation_id)

    if reservation.is_confirmed:
        return redirect("confirmation")

    seat_assignments = SeatAssignment.objects.filter(reservation=reservation)
    if request.method == "POST":
        confirm = request.POST.get("confirm","")

        if confirm == "yes":
            reservation.is_confirmed = True
            reservation.save()
            return redirect("confirmation")

    return render(request, "reservations/review_reservation.html", {"reservation": reservation, "seat_assignments": seat_assignments})

def confirmation(request):
    reservation_id = request.session.get("reservation_id")

    if not reservation_id:
        return redirect("reservation_login")

    reservation = Reservation.objects.get(id=reservation_id)

    if not reservation.is_confirmed:
        return redirect("table_selection")

    seat_assignments = SeatAssignment.objects.filter(reservation=reservation)

    return render(request, "reservations/confirmation.html", {"reservation": reservation, "seat_assignments": seat_assignments})