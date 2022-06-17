from django.urls import path

from api.ticket.views import TicketListView, TicketCreateRowView


urlpatterns = [
    path('ticket/list/<int:event_id>/', TicketListView.as_view(), name='ticket_list'),
    path('ticket/create_row/', TicketCreateRowView.as_view(), name='ticket_create_row')
]
