from django.urls import path

from api.ticket.views import TicketListView


urlpatterns = [
    path('ticket/list/<int:event_id>/', TicketListView.as_view(), name='ticket_list'),
]
