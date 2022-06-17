from rest_framework import generics, permissions, status
from rest_framework.response import Response

from api.event.utilities import CustomPageNumberPagination
from api.ticket.models import Ticket
from api.ticket.serializers import TicketSerializer, TicketCreateRowSerializer


class TicketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        qs = Ticket.objects.filter(event__id=event_id, reservation__isnull=True)
        return qs


class TicketCreateRowView(generics.GenericAPIView):
    """
{
    "event": 1,
    "seats": 0,
    "row": "string",
    "price": 0
}
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = TicketCreateRowSerializer

    def post(self, request, *args, **kwargs):
        # TODO: Should be fixed in DRF library in later versions, check when upgrading requirements
        # https://github.com/encode/django-rest-framework/issues/6254
        if 'row' not in request.data:
            request.data['row'] = None

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
