from django.shortcuts import render

# Create your views here.
def reservation_login(request):
    return render(request, 'reservations/reservation_login.html')