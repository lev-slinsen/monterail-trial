from rest_framework import serializers

from api.ticket.models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['id', 'seat', 'event_row', 'status', 'price']
