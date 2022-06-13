from copy import copy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.event.models import Event, EventRow
from api.reservation.models import Reservation
from api.reservation.payment_gateway import PaymentGateway
from api.ticket.models import Ticket


class ReservationSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        ticket_ids = [ticket.id for ticket in attrs['tickets']]
        tickets = Ticket.objects.filter(id__in=ticket_ids)

        # Validating for same event
        #
        if len(tickets.distinct('event_row__related_event')) > 1:
            raise serializers.ValidationError({'error': 'Selected tickets belong to different events.'})

        # Validating if already reserved
        #
        reservations = tickets.distinct('reservation').values_list('reservation', flat=True)
        if len(reservations) != 1 or reservations[0] is not None:
            raise serializers.ValidationError({'error': 'Selected tickets are not available for purchase.'})

        # Validating availability based on event categories
        #
        event_id = tickets.values_list('event_row__related_event', flat=True).distinct().first()
        event = Event.objects.get(id=event_id)

        if event.category == 'even' and (len(tickets) % 2) != 0:
            raise serializers.ValidationError({'error': 'Number of tickets for this event must be even.'})

        if event.category == 'avoid_one':
            row_ids = tickets.values_list('event_row').distinct()
            rows = EventRow.objects.filter(id__in=row_ids)
            for row in rows:
                available_tickets = row.tickets.all().exclude(id__in=ticket_ids).filter(reservation__isnull=True)
                if len(available_tickets) == 1:
                    raise serializers.ValidationError({'error': "Can't leave a single tickets in a row."})

        if event.category == 'all_together':
            row_ids = tickets.values_list('event_row').distinct()
            rows = EventRow.objects.filter(id__in=row_ids)
            for row in rows:
                row_tickets = tickets & Ticket.objects.filter(event_row=row)
                if len(row_tickets) > 1:
                    diff = row_tickets[0].id
                    for i, ticket in enumerate(row_tickets):
                        if ticket.id - i != diff:
                            raise serializers.ValidationError({'error': "All seats in each row must be near each other."})
        return attrs

    class Meta:
        model = Reservation
        fields = ['id', 'created_at', 'tickets', 'user', 'status']
        read_only_fields = ['id', 'created_at', 'status']


class PaymentSerializer(serializers.Serializer):
    reservation = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)
    token = serializers.CharField(max_length=255, required=True)
    currency = serializers.CharField(max_length=3, required=False)
    user = serializers.IntegerField(required=False)

    def validate(self, attrs):
        # Separating values for payment gateway
        attrs_copy = copy(attrs)
        reservation_id = attrs_copy.pop('reservation')
        user_id = attrs_copy.pop('user')

        # Validating reservation
        #
        reservation = Reservation.objects.filter(id=reservation_id)
        if not reservation:
            raise ValidationError({'error': "Reservation with this ID doesn't exist."})
        reservation = reservation.first()
        if reservation.user.id != user_id:
            raise ValidationError({'error': "Reservation doesn't belong to you."})
        if reservation.status == 'purchased':
            raise ValidationError({'error': "Reservation has already been paid for."})
        if reservation.total_price != attrs['amount']:
            raise ValidationError({'error': "Payment amount has to be the same as price."})

        # Addressing payment gateway
        #
        pgw_values = [attrs_copy[i] for i in attrs_copy]
        pgw = PaymentGateway()
        try:
            pgw_reply = pgw.charge(*pgw_values)
        except Exception as ex:
            raise ValidationError({'error': ex})

        reservation.status = 'purchased'
        reservation.save()

        return attrs

    class Meta:
        model = Reservation
        fields = ['amount', 'token', 'currency']
