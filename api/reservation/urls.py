from django.urls import path

from api.reservation.views import ReservationCreateView, ReservationListView, ReservationPayView


urlpatterns = [
    path('reservation/create/', ReservationCreateView.as_view(), name='reservation_create'),
    path('reservation/my/', ReservationListView.as_view(), name='my_reservations'),
    path('reservation/pay/', ReservationPayView.as_view(), name='reservation_pay')
]
