from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_login, name='reservation_login'),
]