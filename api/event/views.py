from django.utils import timezone
from rest_framework import generics, permissions

from api.event.models import Event
from api.event.serializers import EventSerializer
from api.event.utilities import CustomPageNumberPagination


class EventListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Event.objects.filter(datetime_start__gte=timezone.now()).order_by('-datetime_start')
