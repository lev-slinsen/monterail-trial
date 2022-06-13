from rest_framework import generics, permissions

from api.event.models import EventRow
from api.event.utilities import CustomPageNumberPagination
from api.ticket.models import Ticket
from api.ticket.serializers import TicketSerializer


class TicketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        event_rows = EventRow.objects.filter(related_event=event_id)
        qs = Ticket.objects.filter(event_row__in=event_rows, reservation__isnull=True)
        return qs
