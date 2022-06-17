from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from api.ticket.models import Ticket, create_row


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['id', 'seat', 'row', 'status', 'price']


class TicketCreateRowSerializer(serializers.ModelSerializer):
    seats = serializers.IntegerField()

    class Meta:
        model = Ticket
        fields = ['id', 'event', 'seats', 'row', 'price']

    def validate(self, attrs):
        event = attrs['event']
        seats = attrs['seats']
        row = attrs['row']

        if event.datetime_start < timezone.now():
            raise serializers.ValidationError({'error': 'The event has already started.'})

        if seats <= 0:
            raise serializers.ValidationError({'error': f"Number of seats must be a valid number, can't be {seats}."})

        created = create_row(event=event, seats=seats, row=row, price=attrs['price'])
        if created is not True:
            if settings.DEBUG:
                raise serializers.ValidationError({'error': str(created)})
            raise serializers.ValidationError({'error': "Can't create such row. Probably it already exists."})

        return attrs
