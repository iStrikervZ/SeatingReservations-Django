from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_login, name='reservation_login'),
    path("tables/", views.table_selection, name="table_selection"),
    path("tables/<int:table_id>/", views.seat_selection, name="seat_selection"),
    path("review/",views.review_reservation, name="review_reservation"),
    path("confirmation/", views.confirmation, name="confirmation"),
]