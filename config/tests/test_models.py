from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.event.models import Event
from api.reservation.models import Reservation
from api.ticket.models import Ticket, create_row
from django.db import transaction

User = get_user_model()
now = timezone.now()
tomorrow = now + timedelta(days=1)


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user_1')
        self.event = Event.objects.create(title='event', datetime_start=tomorrow)
        self.reservation = Reservation.objects.create(user=self.user)
        self.seats_per_row = 3

    def test_event(self):
        self.assertEqual(str(self.event), 'event')

    def test_ticket(self):
        create_row(event=self.event, seats=self.seats_per_row, price=1)
        create_row(event=self.event, row='A', seats=self.seats_per_row, price=1)
        tickets = Ticket.objects.filter(event=self.event)

        self.assertEqual(len(tickets), self.seats_per_row*2)
        self.assertEqual(tickets.first().status, None)

        # Creating new tickets with same event and row should fail (need transaction for tests only)
        with transaction.atomic():
            create_row(event=self.event, row='A', seats=self.seats_per_row*3, price=1)
        self.assertEqual(len(tickets), self.seats_per_row*2)

    def test_reservation(self):
        create_row(event=self.event, seats=self.seats_per_row, price=1)
        tickets = Ticket.objects.filter(event=self.event)

        for ticket in tickets:
            ticket.reservation = self.reservation
        Ticket.objects.bulk_update(tickets, fields=['reservation'])

        self.assertEqual(len(tickets.filter(reservation=self.reservation)), len(tickets))
        self.assertEqual(list(tickets.filter(reservation=self.reservation).values_list('reservation')),
                         list(tickets.values_list('reservation')))
